"""
Inventory routes.
Endpoints for managing SKUs, sales logs, and stock levels.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/{store_id}/skus")
async def list_skus(store_id: str):
    """List all SKUs for a store."""
    # TODO: Query SKUs table
    return {"store_id": store_id, "skus": []}


@router.get("/{store_id}/sales")
async def list_sales(store_id: str):
    """List recent sales logs for a store."""
    # TODO: Query sales_logs table
    return {"store_id": store_id, "sales": []}


@router.post("/{store_id}/sales")
async def log_sale(store_id: str):
    """Manually log a sale (used by NLP parser service internally)."""
    # TODO: Accept parsed sale data, insert into sales_logs
    return {"store_id": store_id, "status": "logged"}
