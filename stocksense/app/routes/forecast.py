"""Forecast routes redirect to inventory for consolidated API handling."""

from fastapi import APIRouter
from app.routes.inventory import get_forecast as inventory_get_forecast

router = APIRouter()


@router.get("/api/forecast")
async def get_forecast(*args, **kwargs):
    """Proxy forecast requests to the inventory router implementation."""
    return await inventory_get_forecast(*args, **kwargs)


@router.post("/api/forecast/generate")
async def trigger_forecast(*args, **kwargs):
    """Forecast generation remains unimplemented in this scaffold."""
    return {
        "status": "unavailable",
        "message": "Use /api/forecast for forecast data",
    }
