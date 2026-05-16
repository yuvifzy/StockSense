"""
SKU model — maps to the `skus` table.
Schema from PRD §8: sku_id, store_id, canonical_name, variants[], unit
"""

import uuid

from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import ARRAY

from app.database import Base


class SKU(Base):
    __tablename__ = "skus"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    store_id = Column(
        Integer, ForeignKey("stores.id"), nullable=False, index=True
    )
    canonical_name = Column(String(255), nullable=False)
    variants = Column(ARRAY(String), default=[])  # e.g. ["Maggi 70g", "Maggi masala"]
    unit = Column(String(50), nullable=False, default="units")  # bags, packets, kg, etc.

    def __repr__(self):
        return f"<SKU {self.canonical_name} ({self.unit})>"
