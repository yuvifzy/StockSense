from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime
from app.database import Base

class ReorderSuggestion(Base):
    __tablename__ = "reorder_suggestions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    suggested_qty = Column(Integer, nullable=False)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
