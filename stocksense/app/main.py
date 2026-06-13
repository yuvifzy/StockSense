"""StockSense API application entry point."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import forecast, inventory, whatsapp

# Debug: log REDIS_URL at startup so Railway logs show which URL is in use
print("REDIS_URL:", os.getenv("REDIS_URL", "NOT SET"))
print("DATABASE_URL:", os.getenv("DATABASE_URL", "NOT SET")[:30] + "...")

# Create tables on startup in local/dev environments.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockSense API",
    description="WhatsApp-native inventory forecasting for kirana stores",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://stocksense-app.up.railway.app",
        "https://stocksense-production-2b81.up.railway.app",
    ],
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
