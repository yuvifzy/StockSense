"""
SKU model — maps to the `skus` table.
Schema from PRD §8: sku_id, store_id, canonical_name, variants[], unit
"""

import uuid

from sqlalchemy import Column, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from app.database import Base


class SKU(Base):
    __tablename__ = "skus"

    sku_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    store_id = Column(
        UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True
    )
    canonical_name = Column(String(255), nullable=False)
    # PostgreSQL uses native ARRAY; SQLite falls back to JSON
    variants = Column(ARRAY(String).with_variant(JSON, "sqlite"), default=list)
    # bags, packets, kg, etc.
    unit = Column(String(50), nullable=False, default="units")

    def __repr__(self):
        return f"<SKU {self.canonical_name} ({self.unit})>"
