"""
Forecaster Service — TASK 1
Generates 7-day SKU-level demand forecasts using Facebook Prophet.

PRD references:
  P0.3 — Weekly Demand Forecast
  P0.4 — Reorder Quantity Recommendation
  Risk 4 — Forecast Inaccuracy (always show confidence level)
"""

import logging
import math
import uuid
from datetime import date, timedelta
from typing import Optional, Dict, List

import pandas as pd
from neuralprophet import NeuralProphet
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.sales_log import SalesLog
from app.models.sku import SKU
from app.models.forecast import Forecast, ReorderSuggestion

logger = logging.getLogger(__name__)

# Minimum data thresholds
MIN_DAYS_FOR_FORECAST = 14
MIN_DAYS_FOR_HIGH_CONFIDENCE = 21
DATA_LOOKBACK_DAYS = 60


def _fetch_daily_sales(
    db: Session,
    store_id: int,
    sku_id: int,
    lookback_days: int = DATA_LOOKBACK_DAYS,
) -> pd.DataFrame:
    """
    Pull aggregated daily sales for a single store+sku from the last N days.

    return created
    Generate a 7-day demand forecast for a single store + SKU using Prophet.

    Args:
        db:            SQLAlchemy session
        store_id:      ID of the store
        sku_id:        ID of the SKU
        horizon_days:  Forecast horizon (default 7 days)

    Returns:
        {
            "predicted_qty": int,
            "reorder_qty": int,
            "confidence": str  # "High" | "Medium" | "Low"
        }
        or None if insufficient data (< 14 days).
    """
    logger.info("Generating forecast for store=%s sku=%s", store_id, sku_id)
    sales_df = _fetch_daily_sales(db, store_id, sku_id)

    # Minimum data check (PRD: "Minimum 2 weeks of input data required")
    unique_days = sales_df["ds"].nunique() if not sales_df.empty else 0
    if unique_days < MIN_DAYS_FOR_FORECAST:
        logger.info(
            "Insufficient data for forecast: store=%s sku=%s days=%d (need %d)",
            store_id, sku_id, unique_days, MIN_DAYS_FOR_FORECAST,
        )
        return None

    # Train Prophet on full dataset for the actual forecast
    model = NeuralProphet(
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=False,
    )

    # Add Indian holidays as regressors (PRD §8: "holiday effects via custom calendar")
    try:
        model.add_country_holidays(country_name="IN")
    except Exception as e:
        logger.warning("Could not add Indian holidays: %s", e)

    metrics = model.fit(sales_df)

    # Calculate confidence based on NeuralProphet metrics
    last_mae = metrics["MAE"].iloc[-1]
    mean_actual = sales_df["y"].mean()
    mae_pct = last_mae / mean_actual if mean_actual > 0 else 1.0

    days_of_data = len(sales_df)
    confidence = _calculate_confidence(mae_pct, days_of_data)

    # Generate future predictions
    future = model.make_future_dataframe(df=sales_df, periods=horizon_days)
    forecast = model.predict(future)

    # Sum predicted demand for the next `horizon_days`
    future_preds = forecast.tail(horizon_days)
    predicted_qty = max(0, int(round(future_preds["yhat1"].sum())))

    # Reorder quantity = ceil(predicted_qty × 1.2) — PRD P0.4 safety buffer
    reorder_qty = math.ceil(predicted_qty * 1.2)

    logger.info(
        "Forecast: store=%s sku=%s predicted=%d reorder=%d confidence=%s",
        store_id, sku_id, predicted_qty, reorder_qty, confidence,
    )

    return {
        "predicted_qty": predicted_qty,
        "reorder_qty": reorder_qty,
        "confidence": confidence,
    }


def generate_all_forecasts(
    db: Session,
    store_id: int,
    horizon_days: int = 7,
) -> List[Dict]:
    """
    Generate forecasts for ALL SKUs belonging to a store that have ≥14 days of data.

    Returns a list of dicts:
    [
        {
            "sku_id": int,
            "sku_name": str,
            "unit": str,
            "predicted_qty": int,
            "reorder_qty": int,
            "confidence": str,
        },
        ...
    ]
    """
    skus = db.query(SKU).filter(SKU.store_id == store_id).all()
    results = []

    for sku in skus:
        forecast = generate_forecast(db, store_id, sku.id, horizon_days)
        if forecast is not None:
            results.append({
                "sku_id": sku.id,
                "sku_name": sku.canonical_name,
                "unit": sku.unit,
                **forecast,
            })

    # Sort by reorder urgency (highest reorder_qty first)
    results.sort(key=lambda x: x["reorder_qty"], reverse=True)
    return results


def get_deadstock_skus(
    db: Session,
    store_id: int,
    days: int = 14,
) -> List[Dict]:
    """
    Find SKUs with ZERO sales in the last `days` days.
    These are deadstock candidates per PRD P1.2.

    Returns:
        [{"sku_id": int, "sku_name": str, "days_since_last_sale": int}, ...]
    """
    cutoff = date.today() - timedelta(days=days)

    # All SKUs for this store
    all_skus = db.query(SKU).filter(SKU.store_id == store_id).all()

    # SKUs that had at least one sale in the last `days` days
    active_sku_ids = (
        db.query(SalesLog.sku_id)
        .filter(
            SalesLog.store_id == store_id,
            SalesLog.date >= cutoff,
        )
        .distinct()
        .all()
    )
    active_ids = {row[0] for row in active_sku_ids}

    deadstock = []
    for sku in all_skus:
        if sku.id not in active_ids:
            # Find last sale date for context
            last_sale = (
                db.query(func.max(SalesLog.date))
                .filter(
                    SalesLog.store_id == store_id,
                    SalesLog.sku_id == sku.id,
                )
                .scalar()
            )
            days_since = (date.today() - last_sale).days if last_sale else 999
            deadstock.append({
                "sku_id": sku.id,
                "sku_name": sku.canonical_name,
                "days_since_last_sale": days_since,
            })

    return deadstock


def persist_forecast_to_db(
    db: Session,
    store_id: int,
    week_start: date,
    forecast_results: List[Dict],
) -> List[Forecast]:
    """
    Save forecast results to the forecasts + reorder_suggestions tables.
    """
    created = []

    for item in forecast_results:
        fc = Forecast(
            store_id=store_id,
            week_start=week_start,
            sku_id=item["sku_id"],
            predicted_qty=item["predicted_qty"],
            confidence=item["confidence"],
        )
        db.add(fc)
        db.flush()  # Get forecast_id

        reorder = ReorderSuggestion(
            forecast_id=fc.id,
            sku_id=item["sku_id"],
            suggested_qty=item["reorder_qty"],
            confirmed=False,
        )
        db.add(reorder)
        created.append(fc)

    db.commit()
    logger.info(
        "Persisted %d forecasts for store %s (week %s)",
        len(created), store_id, week_start,
    )
    return created
