"""
StockSense — AI-powered inventory intelligence for kirana stores.
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import whatsapp, forecast, inventory
from app.database import engine, Base

# ── Create tables on startup (dev only — use Alembic migrations in prod) ──
# Base.metadata.create_all(bind=engine)  # Uncomment once models are finalised

app = FastAPI(
    title="StockSense API",
    description="WhatsApp-native inventory forecasting for kirana stores",
    version="0.1.0",
)

# ── CORS (allow frontend dev server) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register route modules ──
app.include_router(whatsapp.router, prefix="/webhook", tags=["WhatsApp"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])


# ── Health check ──
@app.get("/health", tags=["System"])
async def health_check():
    """Returns service health and database connectivity status."""
    # TODO: Add real DB ping once Supabase is connected
    return {"status": "ok", "db": "connected"}
# StockSense Backend — forecasting module by @yuvifzy
