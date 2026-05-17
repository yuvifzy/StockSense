"""Sales log model."""

from datetime import date as date_type

from sqlalchemy import Column, Integer, ForeignKey, Date, String

from app.database import Base


class SalesLog(Base):
    __tablename__ = "sales_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    date = Column(Date, default=date_type.today, nullable=False)
    source = Column(String(20), default="text", nullable=False)
