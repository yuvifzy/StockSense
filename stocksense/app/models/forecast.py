"""Forecast model."""

from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, String, DateTime

from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    week_start = Column(DateTime, nullable=False)
    predicted_qty = Column(Integer, nullable=False)
    reorder_qty = Column(Integer, nullable=False)
    confidence = Column(String(10), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
