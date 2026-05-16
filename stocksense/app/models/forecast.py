"""
Forecast & ReorderSuggestion models.
Schema from PRD §8:
  forecasts       — forecast_id, store_id, week_start, sku_id, predicted_qty, confidence, generated_at
  reorder_suggestions — suggestion_id, forecast_id, sku_id, suggested_qty, confirmed
"""

import uuid
from datetime import datetime, date as date_type

from sqlalchemy import Column, Integer, Float, String, Boolean, Date, DateTime, ForeignKey

from app.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    store_id = Column(
        Integer, ForeignKey("stores.id"), nullable=False, index=True
    )
    week_start = Column(Date, nullable=False)
    sku_id = Column(
        Integer, ForeignKey("skus.id"), nullable=False, index=True
    )
    predicted_qty = Column(Float, nullable=False)
    confidence = Column(
        String(10), nullable=False, default="medium"
    )  # high | medium | low
    generated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Forecast store={self.store_id} sku={self.sku_id} qty={self.predicted_qty}>"


class ReorderSuggestion(Base):
    __tablename__ = "reorder_suggestions"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    forecast_id = Column(
        Integer,
        ForeignKey("forecasts.id"),
        nullable=False,
        index=True,
    )
    sku_id = Column(
        Integer, ForeignKey("skus.id"), nullable=False, index=True
    )
    suggested_qty = Column(Integer, nullable=False)
    confirmed = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Reorder sku={self.sku_id} qty={self.suggested_qty} confirmed={self.confirmed}>"
