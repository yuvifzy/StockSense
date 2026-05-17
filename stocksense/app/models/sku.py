"""SKU model."""

from sqlalchemy import Column, String, Integer, ForeignKey

from app.database import Base


class SKU(Base):
    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    canonical_name = Column(String(255), nullable=False)
    unit = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<SKU {self.canonical_name}>"
