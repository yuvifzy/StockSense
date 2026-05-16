"""
SalesLog model — maps to the `sales_logs` table.
Schema from PRD §8: log_id, store_id, sku_id, quantity_sold, date, source
"""

import uuid
from datetime import date as date_type

from sqlalchemy import Column, Integer, Date, String, ForeignKey


from app.database import Base


class SalesLog(Base):
    __tablename__ = "sales_logs"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    store_id = Column(
        Integer, ForeignKey("stores.id"), nullable=False, index=True
    )
    sku_id = Column(
        Integer, ForeignKey("skus.id"), nullable=False, index=True
    )
    quantity_sold = Column(Integer, nullable=False)
    date = Column(Date, default=date_type.today, nullable=False)
    source = Column(
        String(20), nullable=False, default="text"
    )  # text | ocr | voice

    def __repr__(self):
        return f"<SalesLog store={self.store_id} sku={self.sku_id} qty={self.quantity_sold}>"
