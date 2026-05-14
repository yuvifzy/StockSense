"""
Forecast routes.
Endpoints for triggering and retrieving demand forecasts.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{store_id}")
async def get_forecast(store_id: str):
    """
    Retrieve the latest weekly forecast for a given store.
    """
    # TODO: Query forecasts table, return latest forecast for store
    return {
        "store_id": store_id,
        "forecast": [],
        "message": "Forecast endpoint scaffold — no logic yet",
    }


@router.post("/{store_id}/generate")
async def generate_forecast(store_id: str):
    """
    Trigger on-demand forecast generation for a store.
    """
    # TODO: Enqueue Celery task → Prophet pipeline
    return {
        "store_id": store_id,
        "status": "queued",
        "message": "Forecast generation scaffold — no logic yet",
    }
