"""
Forecast routes — TASK 3
Endpoints for triggering and retrieving demand forecasts.

GET /api/forecast?store_id=X&week=YYYY-MM-DD
  Returns JSON array of forecast results with status field.
"""

import uuid
from datetime import date, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.forecast import Forecast, ReorderSuggestion
from app.models.sku import SKU
from app.services.forecaster import generate_all_forecasts, persist_forecast_to_db

router = APIRouter()


def _get_status(reorder_qty: int, current_stock: int = 0) -> str:
    """
    Map reorder recommendation to a human-readable status.

    Status field:
      reorder_qty > 0 and stock <= 5  → "Order now"
      reorder_qty > 0 and stock <= 10 → "Order soon"
      reorder_qty == 0                → "Sufficient"
    """
    if reorder_qty == 0:
        return "Sufficient"
    if current_stock <= 5:
        return "Order now"
    if current_stock <= 10:
        return "Order soon"
    return "Sufficient"


@router.get("/api/forecast")
async def get_forecast(
    store_id: int = Query(..., description="Store ID"),
    week: Optional[str] = Query(None, description="Week start date (YYYY-MM-DD). Defaults to current week."),
    db: Session = Depends(get_db),
):
    """
    Retrieve the weekly forecast for a given store.

    Returns JSON array:
    [{ sku_name, predicted_qty, reorder_qty, confidence, status }]
    """
    # Parse week or default to current Monday
    if week:
        try:
            week_start = date.fromisoformat(week)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid week format. Use YYYY-MM-DD.",
            )
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    # Query existing forecasts for this store + week
    forecasts = (
        db.query(Forecast)
        .filter(
            Forecast.store_id == store_id,
            Forecast.week_start == week_start,
        )
        .all()
    )

    if not forecasts:
        # No pre-computed forecast — generate on-demand
        results = generate_all_forecasts(db, store_id)
        if results:
            persist_forecast_to_db(db, store_id, week_start, results)
            return [
                {
                    "sku_name": r["sku_name"],
                    "predicted_qty": r["predicted_qty"],
                    "reorder_qty": r["reorder_qty"],
                    "confidence": r["confidence"],
                    "status": _get_status(r["reorder_qty"]),
                }
                for r in results
            ]
        return []

    # Build response from DB records
    result = []
    for fc in forecasts:
        # Get SKU details
        sku = db.query(SKU).filter(SKU.id == fc.sku_id).first()
        sku_name = sku.canonical_name if sku else "Unknown"

        # Get reorder suggestion
        reorder = (
            db.query(ReorderSuggestion)
            .filter(ReorderSuggestion.forecast_id == fc.id)
            .first()
        )
        reorder_qty = reorder.suggested_qty if reorder else 0

        result.append({
            "sku_name": sku_name,
            "predicted_qty": int(fc.predicted_qty),
            "reorder_qty": reorder_qty,
            "confidence": fc.confidence,
            "status": _get_status(reorder_qty),
        })

    # Sort by reorder urgency
    result.sort(key=lambda x: x["reorder_qty"], reverse=True)
    return result


@router.post("/api/forecast/generate")
async def trigger_forecast(
    store_id: int = Query(..., description="Store ID"),
    db: Session = Depends(get_db),
):
    """
    Trigger on-demand forecast generation for a store.
    Generates forecasts for all qualified SKUs and persists to DB.
    """
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    results = generate_all_forecasts(db, store_id)
    if results:
        persist_forecast_to_db(db, store_id, week_start, results)

    return {
        "store_id": store_id,
        "week_start": week_start.isoformat(),
        "forecasts_generated": len(results),
        "status": "completed",
    }
