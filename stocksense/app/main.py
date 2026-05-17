from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import whatsapp, forecast, inventory
from app.database import engine, Base

app = FastAPI(
    title="StockSense API",
    description="WhatsApp-native inventory forecasting for kirana stores",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(whatsapp.router, prefix="/webhook", tags=["WhatsApp"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(inventory.router, prefix="/api", tags=["Inventory"])

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "db": "connected"}
