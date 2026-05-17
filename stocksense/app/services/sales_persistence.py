from typing import Optional
"""
Sales persistence service — TASK 4
Handles writing confirmed sales to the database.
Creates SKUs on-the-fly if they don't exist for the store.
"""

import logging
import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.models.sku import SKU
from app.models.sales_log import SalesLog

logger = logging.getLogger(__name__)


def get_or_create_sku(
    db: Session,
    store_id: uuid.UUID,
    sku_name: str,
    unit: Optional[str] = None,
) -> SKU:
    """
    Find an existing SKU by canonical_name for this store, or create one.

    Args:
        db:        SQLAlchemy session
        store_id:  UUID of the store
        sku_name:  SKU name as parsed from the user message
        unit:      Unit of measurement (bags, packets, kg, etc.)

    Returns:
        SKU ORM instance (existing or newly created)
    """
    # Normalise name for matching (lowercase, strip whitespace)
    normalised = sku_name.strip().lower()

    existing = (
        db.query(SKU)
        .filter(
            SKU.store_id == store_id,
            SKU.canonical_name.ilike(normalised),
        )
        .first()
    )

    if existing:
        return existing

    new_sku = SKU(
        store_id=store_id,
        canonical_name=normalised,
        variants=[sku_name.strip()],   # Keep original form as a variant
        unit=unit or "units",
    )
    db.add(new_sku)
    db.flush()  # Assign sku_id without committing
    logger.info("Created new SKU '%s' for store %s", normalised, store_id)
    return new_sku


def persist_sales(
    db: Session,
    store_id: uuid.UUID,
    parsed_items: list[dict],
    source: str = "text",
) -> list[SalesLog]:
    """
    Write confirmed sales to the database.

    For each parsed item:
      1. Find or create the SKU for this store
      2. Insert a SalesLog record

    Args:
        db:            SQLAlchemy session
        store_id:      UUID of the store
        parsed_items:  Output from nlp_parser (confirmed by user)
        source:        Input source — "text", "ocr", or "voice"

    Returns:
        List of created SalesLog records
    """
    created_logs = []

    for item in parsed_items:
        sku_name = item.get("sku_name", "").strip()
        quantity = item.get("quantity", 1)
        unit = item.get("unit")

        if not sku_name:
            continue

        # Get or create SKU
        sku = get_or_create_sku(db, store_id, sku_name, unit)

        # Create sales log
        log = SalesLog(
            store_id=store_id,
            sku_id=sku.sku_id,
            quantity_sold=quantity,
            date=date.today(),
            source=source,
        )
        db.add(log)
        created_logs.append(log)

    # Commit all at once
    db.commit()
    logger.info(
        "Persisted %d sales records for store %s",
        len(created_logs), store_id,
    )
    return created_logs
