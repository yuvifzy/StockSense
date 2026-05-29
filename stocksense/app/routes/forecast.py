"""Forecast routes for API scaffolding."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/api/forecast")
async def get_forecast(store_id: int = Query(..., gt=0)):
    """Return an empty forecast payload for now."""
    return {"store_id": store_id, "forecasts": []}


@router.post("/api/forecast/generate")
async def trigger_forecast(*args, **kwargs):
    """Forecast generation remains unimplemented in this scaffold."""
    return {
        "status": "unavailable",
        "message": "Use /api/forecast for forecast data",
    }
