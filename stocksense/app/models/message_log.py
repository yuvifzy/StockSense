"""MessageLog model for storing inbound/outbound WhatsApp messages."""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from app.database import Base


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"),
                      nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # inbound | outbound
    text = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self) -> str:
        return f"<MessageLog store={self.store_id} direction={self.direction}>"
