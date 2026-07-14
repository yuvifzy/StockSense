"""
Celery tasks for StockSense — TASK 2

Task 1: send_weekly_forecast
  - Schedule: every Monday 8:00 AM IST (Asia/Kolkata)
  - For each active store, generate forecasts for all SKUs with ≥14 days data
  - Build WhatsApp message (top 15 SKUs sorted by reorder urgency)
  - Append deadstock alert for any SKU with 0 sales in last 14 days
  - Send via messenger.send_text()

Task 2: send_daily_reminder
  - Schedule: every day 9:00 PM IST
  - For each store with no sales_log entry today, send nudge in their language
  - Skip if store has reminder_paused = true

PRD references: P0.3, P1.1, §7 (forecast message format), §8 (Celery Beat)
"""

import asyncio
import logging
from datetime import date, timedelta
from typing import List, Dict

from celery import Celery
from celery.schedules import crontab

from app.config import settings
from app.database import SessionLocal
from app.models.store import Store
from app.models.sales_log import SalesLog
from app.services.forecaster import (
    generate_all_forecasts,
    get_deadstock_skus,
    persist_forecast_to_db,
)
from app.services.messenger import send_text

logger = logging.getLogger(__name__)

# ── Celery app config ──
logger.info("Celery broker/backend: %s", settings.REDIS_URL[:30] + "...")

celery_app = Celery(
    "stocksense",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.timezone = "Asia/Kolkata"
celery_app.conf.enable_utc = True

# ── Beat schedule (cron jobs) ──
# Weekly forecast runs Monday 8:00 AM IST.
# Daily reminder runs every day at 9:00 PM IST.
celery_app.conf.beat_schedule = {
    "weekly-forecast-monday-8am": {
        "task": "app.tasks.send_weekly_forecast",
        "schedule": crontab(
            hour=8, minute=0, day_of_week=1,  # Monday = 1
        ),
    },
    "daily-reminder-9pm": {
        "task": "app.tasks.send_daily_reminder",
        "schedule": crontab(hour=21, minute=0),  # 9 PM daily
    },
}

# ── Multi-language templates for forecast messages ──
FORECAST_HEADER = {
    "hi": "🔮 Is hafte ka forecast ({date_range}):\n\nTOP SKUs jinhein ORDER KARNA CHAHIYE:\n",
    "ta": "🔮 இந்த வாரத்தின் forecast ({date_range}):\n\nORDER செய்ய வேண்டிய TOP SKUs:\n",
    "en": "🔮 This week's forecast ({date_range}):\n\nTOP SKUs TO ORDER:\n",
}

CONFIDENCE_ICONS = {
    "High": "✅",
    "Medium": "🟡",
    "Low": "🔴",
}

DEADSTOCK_HEADER = {
    "hi": "\n⚠️ DEADSTOCK ALERT:",
    "ta": "\n⚠️ DEADSTOCK ALERT:",
    "en": "\n⚠️ DEADSTOCK ALERT:",
}

DEADSTOCK_LINE = {
    "hi": "{name} — {days} din se nahi bika. Order mat karna.",
    "ta": "{name} — {days} நாட்களாக விற்கவில்லை. Order செய்யாதீர்கள்.",
    "en": "{name} — no sales in {days} days. Don't order.",
}

FORECAST_FOOTER = {
    "hi": "\nConfirm karna ho toh reply karein: CONFIRM\nChanges ke liye: koi bhi item ka naam aur quantity bhejein.",
    "ta": "\nConfirm செய்ய reply செய்யுங்கள்: CONFIRM\nமாற்றங்களுக்கு: பொருள் பெயர் மற்றும் quantity அனுப்புங்கள்.",
    "en": "\nReply CONFIRM to confirm.\nFor changes: send item name and quantity.",
}

DAILY_REMINDER = {
    "hi": "Aaj ki sales share karna bhool gaye? Abhi bhej dein! 🛒",
    "ta": "இன்றைய sales share செய்ய மறந்துவிட்டீர்களா? இப்போது அனுப்புங்கள்! 🛒",
    "en": "Forgot to share today's sales? Send them now! 🛒",
}


def _format_forecast_message(
    forecasts: List[Dict],
    deadstock: List[Dict],
    lang: str,
    week_start: date,
) -> str:
    """
    Build the WhatsApp forecast message exactly as PRD §7 specifies.

    Format:
      "🔮 Is hafte ka forecast (15–21 May):
       1. Atta 5kg → 18 bags expect | Order: 20 bags [High ✅]
       ⚠️ DEADSTOCK: [item] — 14 din se nahi bika"
    """
    week_end = week_start + timedelta(days=6)
    date_range = f"{week_start.strftime('%d %b')}–{week_end.strftime('%d %b')}"

    header = FORECAST_HEADER.get(lang, FORECAST_HEADER["hi"]).format(
        date_range=date_range
    )
    lines = [header]

    # Top 15 SKUs sorted by reorder urgency
    top_skus = forecasts[:15]
    for i, item in enumerate(top_skus, 1):
        confidence = item.get("confidence", "Low")
        icon = CONFIDENCE_ICONS.get(confidence, "🔴")
        unit = item.get("unit", "units")
        lines.append(
            f"{i}. {item['sku_name'].title():<20s} → {item['predicted_qty']} {unit} expect"
            f"  | Order: {item['reorder_qty']} {unit}  [{confidence} {icon}]"
        )

    # Deadstock alerts
    if deadstock:
        lines.append(DEADSTOCK_HEADER.get(lang, DEADSTOCK_HEADER["hi"]))
        for ds in deadstock[:5]:  # Max 5 per PRD P1.2
            line_template = DEADSTOCK_LINE.get(lang, DEADSTOCK_LINE["hi"])
            lines.append(line_template.format(
                name=ds["sku_name"].title(),
                days=ds["days_since_last_sale"],
            ))

    lines.append(FORECAST_FOOTER.get(lang, FORECAST_FOOTER["hi"]))
    return "\n".join(lines)


def _run_async(coro):
    """Helper to run an async function from sync Celery task context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop for the task
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


@celery_app.task(name="app.tasks.send_weekly_forecast")
def send_weekly_forecast():
    """
    Weekly forecast task — runs every Monday 8:00 AM IST.

    For each ACTIVE store:
      1. Generate Prophet forecasts for all qualified SKUs
      2. Detect deadstock (0 sales in 14 days)
      3. Persist forecasts to DB
      4. Build formatted WhatsApp message (top 15 SKUs)
      5. Send via WhatsApp
    """
    db = SessionLocal()
    try:
        stores = db.query(Store).all()
        today = date.today()
        # Monday of this week
        week_start = today - timedelta(days=today.weekday())

        logger.info(
            "Starting weekly forecast for %d stores (week: %s)",
            len(stores), week_start,
        )

        for store in stores:
            try:
                # Generate forecasts for all SKUs
                try:
                    forecasts = generate_all_forecasts(db, store.id)
                except Exception as e:
                    logger.error(
                        "Forecast generation failed for store %s: %s",
                        store.name, e, exc_info=True,
                    )
                    continue
                if not forecasts:
                    logger.info(
                        "No forecastable SKUs for store %s", store.name
                    )
                    continue

                # Detect deadstock
                deadstock = get_deadstock_skus(db, store.id)

                # Persist to DB
                persist_forecast_to_db(
                    db, store.id, week_start, forecasts
                )

                # Build and send message
                lang = store.language or "hi"
                message = _format_forecast_message(
                    forecasts, deadstock, lang, week_start
                )
                _run_async(send_text(store.whatsapp_number, message))

                logger.info(
                    "Sent weekly forecast to %s (%d SKUs, %d deadstock)",
                    store.name, len(forecasts), len(deadstock),
                )

            except Exception as e:
                logger.error(
                    "Failed to generate forecast for store %s: %s",
                    store.name, e, exc_info=True,
                )
                continue

    finally:
        db.close()


@celery_app.task(name="app.tasks.send_daily_reminder")
def send_daily_reminder():
    """
    Daily reminder task — runs every day at 9:00 PM IST.

    For each store that has NOT logged any sales today:
      - Send a nudge in their preferred language
      - Skip if store has reminder_paused = True
    """
    db = SessionLocal()
    try:
        today = date.today()
        stores = db.query(Store).all()

        logger.info("Checking %d stores for daily reminder", len(stores))

        for store in stores:
            try:
                # Check if reminder is paused (check for attribute safely)
                if getattr(store, "reminder_paused", False):
                    continue

                # Check if store logged any sales today
                today_sales = (
                    db.query(SalesLog)
                    .filter(
                        SalesLog.store_id == store.id,
                        SalesLog.date == today,
                    )
                    .first()
                )

                if today_sales is not None:
                    continue  # Already logged sales today

                # Send reminder in user's preferred language
                lang = store.language or "hi"
                reminder = DAILY_REMINDER.get(lang, DAILY_REMINDER["hi"])
                _run_async(send_text(store.whatsapp_number, reminder))

                logger.info(
                    "Sent daily reminder to %s (%s)",
                    store.name, store.whatsapp_number,
                )

            except Exception as e:
                logger.error(
                    "Failed to send reminder to store %s: %s",
                    store.name, e, exc_info=True,
                )
                continue

    finally:
        db.close()
