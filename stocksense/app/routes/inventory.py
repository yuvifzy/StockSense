"""
Inventory routes — TASK 4
Endpoints for SKU management, stock levels, and store statistics.

GET /api/inventory?store_id=X
  Returns all SKUs for this store with current stock, avg daily sales, days remaining.

GET /api/stats?store_id=X
  Returns: { reorder_count, deadstock_count, forecast_accuracy, savings_inr }
"""

import uuid
from datetime import date, timedelta
from typing import Optional, Dict

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sku import SKU
from app.models.sales_log import SalesLog
from app.models.forecast import Forecast, ReorderSuggestion
from app.services.forecaster import get_deadstock_skus

router = APIRouter()


@router.get("/api/inventory")
def get_inventory(
    store_id: int = Query(..., description="ID of the store"),
    db: Session = Depends(get_db),
):
    """
    Returns all SKUs for this store with:
      - current_stock (estimated from declared stock minus cumulative sales)
      - avg_daily_sales (last 30 days)
      - days_remaining (current_stock / avg_daily_sales)
    """
    skus = db.query(SKU).filter(SKU.store_id == store_id).all()
    if not skus:
        return []

    cutoff_30d = date.today() - timedelta(days=30)
    result = []

    for sku in skus:
        # Calculate average daily sales over last 30 days
        total_sold_30d = (
            db.query(func.coalesce(func.sum(SalesLog.quantity_sold), 0))
            .filter(
                SalesLog.store_id == store_id,
                SalesLog.sku_id == sku.id,
                SalesLog.date >= cutoff_30d,
            )
            .scalar()
        )

        # Count distinct days with sales data
        days_with_data = (
            db.query(func.count(func.distinct(SalesLog.date)))
            .filter(
                SalesLog.store_id == store_id,
                SalesLog.sku_id == sku.id,
                SalesLog.date >= cutoff_30d,
            )
            .scalar()
        ) or 0

        avg_daily = round(total_sold_30d / max(days_with_data, 1), 1)

        # Total lifetime sales as a rough stock proxy
        # (Real stock tracking requires P1.4 — current stock input)
        total_lifetime = (
            db.query(func.coalesce(func.sum(SalesLog.quantity_sold), 0))
            .filter(
                SalesLog.store_id == store_id,
                SalesLog.sku_id == sku.id,
            )
            .scalar()
        )

        # Estimated current stock = 0 (no stock input feature yet)
        # Days remaining is calculated when stock data is available (P1.4)
        current_stock = 0
        days_remaining = 0 if avg_daily == 0 else round(current_stock / avg_daily, 1)

        result.append({
            "sku_id": sku.id,
            "sku_name": sku.canonical_name,
            "unit": sku.unit,
            "current_stock": current_stock,
            "avg_daily_sales": avg_daily,
            "days_remaining": days_remaining,
            "total_sold_30d": int(total_sold_30d),
            "total_sold_lifetime": int(total_lifetime),
        })

    # Sort by avg daily sales (highest first)
    result.sort(key=lambda x: x["avg_daily_sales"], reverse=True)
    return result


@router.get("/api/stats")
def get_stats(
    store_id: int = Query(..., description="ID of the store"),
    db: Session = Depends(get_db),
):
    """
    Returns store-level statistics:
    {
        reorder_count:       Number of SKUs currently needing reorder
        deadstock_count:     Number of SKUs with 0 sales in last 14 days
        forecast_accuracy:   Average confidence across latest forecasts
        savings_inr:         Estimated savings in INR
    }

    savings_inr formula:
      deadstock_items_avoided × 150 + stockouts_prevented × avg_daily_sale × 2
    """
    # Get deadstock count
    deadstock = get_deadstock_skus(db, store_id)
    deadstock_count = len(deadstock)

    # Get latest forecast week
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    latest_forecasts = (
        db.query(Forecast)
        .filter(Forecast.store_id == store_id)
        .order_by(desc(Forecast.generated_at))
        .limit(50)
        .all()
    )

    # Count SKUs needing reorder (those with reorder suggestions)
    reorder_count = 0
    confidence_scores = []

    for fc in latest_forecasts:
        reorder = (
            db.query(ReorderSuggestion)
            .filter(ReorderSuggestion.forecast_id == fc.id)
            .first()
        )
        if reorder and reorder.suggested_qty > 0:
            reorder_count += 1

        # Map confidence to numeric for averaging
        conf_map = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
        confidence_scores.append(conf_map.get(fc.confidence, 0.3))

    # Forecast accuracy as average confidence percentage
    forecast_accuracy = (
        round(sum(confidence_scores) / len(confidence_scores) * 100, 1)
        if confidence_scores
        else 0.0
    )

    # Calculate estimated savings (INR)
    # deadstock_items_avoided × 150 + stockouts_prevented × avg_daily_sale × 2
    cutoff_30d = date.today() - timedelta(days=30)
    avg_daily_sales_store = (
        db.query(func.coalesce(func.avg(SalesLog.quantity_sold), 0))
        .filter(
            SalesLog.store_id == store_id,
            SalesLog.date >= cutoff_30d,
        )
        .scalar()
    ) or 0

    # Estimate: each confirmed reorder prevents a stockout
    stockouts_prevented = sum(
        1
        for fc in latest_forecasts
        if db.query(ReorderSuggestion)
        .filter(
            ReorderSuggestion.forecast_id == fc.id,
            ReorderSuggestion.confirmed == True,
        )
        .first()
    )

    savings_inr = int(
        deadstock_count * 150
        + stockouts_prevented * float(avg_daily_sales_store) * 2
    )

    return {
        "store_id": store_id,
        "reorder_count": reorder_count,
        "deadstock_count": deadstock_count,
        "forecast_accuracy": forecast_accuracy,
        "savings_inr": savings_inr,
    }


@router.get("/api/stores")
def get_stores(db: Session = Depends(get_db)):
    """
    Returns all registered stores.
    """
    from app.models.store import Store
    stores = db.query(Store).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "pin_code": s.pin_code,
            "language": s.language,
            "created_at": s.created_at,
        }
        for s in stores
    ]
