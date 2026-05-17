"""Store model."""

from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Boolean

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    whatsapp_number = Column(String(20), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    pin_code = Column(String(10), nullable=False)
    language = Column(String(10), default="en", nullable=False)
    reminder_paused = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Store {self.name}>"
