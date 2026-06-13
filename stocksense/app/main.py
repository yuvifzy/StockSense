"""StockSense API application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import forecast, inventory, whatsapp

# Create tables on startup in local/dev environments.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense API",
    description="WhatsApp-native inventory forecasting for kirana stores",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "https://stocksense-app.up.railway.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(whatsapp.router, prefix="/webhook", tags=["WhatsApp"])
app.include_router(forecast.router, tags=["Forecast"])
app.include_router(inventory.router, tags=["Inventory"])


@app.get("/health", tags=["System"])
async def health_check():
    """Return service health status."""
    return {"status": "ok", "db": "connected"}
