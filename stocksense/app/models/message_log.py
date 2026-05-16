"""
MessageLog model — maps to the `message_logs` table.
Schema for GET /api/messages?store_id=X&limit=20
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from app.database import Base


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    store_id = Column(
        Integer, ForeignKey("stores.id"), nullable=False, index=True
    )
    text = Column(String, nullable=False)
    direction = Column(String, nullable=False)  # "inbound" or "outbound"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<MessageLog store={self.store_id} direction={self.direction}>"
