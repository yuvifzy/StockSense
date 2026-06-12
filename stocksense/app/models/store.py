"""
Store model — maps to the `stores` table.
Schema from PRD §8: store_id, whatsapp_number, name, pin_code, language, created_at
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    whatsapp_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    pin_code = Column(String(10), nullable=False)
    language = Column(String(10), nullable=False, default="en")  # en | hi | ta
    reminder_paused = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Store {self.name} ({self.whatsapp_number})>"
