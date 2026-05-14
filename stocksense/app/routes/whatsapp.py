"""
WhatsApp webhook routes — TASK 3 & 4

GET  /webhook  — Meta verification handshake
POST /webhook  — Incoming message receiver + onboarding state machine

State machine flow (Redis-backed):
  NEW → LANG_SELECT → NAME_INPUT → PINCODE → CONFIRMED → ACTIVE
  ACTIVE ↔ AWAITING_CONFIRMATION (sales confirm/reject cycle)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.store import Store
from app.services.conversation import (
    ConversationState,
    get_state,
    set_state,
    get_user_data,
    update_user_data,
    set_pending_items,
    get_pending_items,
    clear_pending_items,
)
from app.services.messenger import get_message, send_text, send_confirmation
from app.services.nlp_parser import parse_sales_message
from app.services.sales_persistence import persist_sales

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Affirmative / negative detection ──
AFFIRMATIVES = {"haan", "ha", "yes", "confirm", "sahi", "ok", "haa", "aam", "aamaa", "ஆமா"}
NEGATIVES = {"nahi", "nah", "no", "galat", "nhi", "wrong", "இல்ல", "illa"}
LANG_MAP = {"1": "hi", "2": "ta", "3": "en", "hindi": "hi", "tamil": "ta", "english": "en"}


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    WhatsApp webhook verification (Meta handshake).
    Meta sends a GET with hub.mode, hub.challenge, and hub.verify_token.
    We return the challenge if the token matches.
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Verification failed", status_code=403)


@router.post("")
async def receive_message(request: Request, db: Session = Depends(get_db)):
    """
    Receives incoming WhatsApp messages from Meta Cloud API.
    Routes the message through the onboarding state machine.
    """
    body = await request.json()

    # ── Extract message data from Meta webhook payload ──
    phone, message_text = _extract_message(body)
    if not phone or not message_text:
        return {"status": "ignored"}

    logger.info("Received from %s: %s", phone, message_text[:100])

    # ── Get current conversation state ──
    state = await get_state(phone)

    # ── Route through state machine ──
    try:
        if state == ConversationState.NEW:
            await _handle_new(phone)

        elif state == ConversationState.LANG_SELECT:
            await _handle_lang_select(phone, message_text)

        elif state == ConversationState.NAME_INPUT:
            await _handle_name_input(phone, message_text)

        elif state == ConversationState.PINCODE:
            await _handle_pincode(phone, message_text, db)

        elif state == ConversationState.AWAITING_CONFIRMATION:
            await _handle_confirmation(phone, message_text, db)

        elif state == ConversationState.ACTIVE:
            await _handle_active(phone, message_text, db)

        else:
            # Unknown state — reset to NEW
            logger.warning("Unknown state '%s' for %s, resetting", state, phone)
            await _handle_new(phone)

    except Exception as e:
        logger.error("Error processing message from %s: %s", phone, e, exc_info=True)
        await send_text(phone, get_message("parse_error", "hi"))

    return {"status": "received"}


# ════════════════════════════════════════════════════
# State handlers
# ════════════════════════════════════════════════════

async def _handle_new(phone: str) -> None:
    """
    NEW state — User sends first message (Hi, Namaste, etc.)
    Response: Language selection prompt
    Transition: NEW → LANG_SELECT
    """
    # Send welcome in Hindi (default) — it includes all 3 language options
    await send_text(phone, get_message("welcome", "hi"))
    await set_state(phone, ConversationState.LANG_SELECT)


async def _handle_lang_select(phone: str, text: str) -> None:
    """
    LANG_SELECT — User picks a language (1/2/3 or Hindi/Tamil/English)
    Response: Ask for store name in selected language
    Transition: LANG_SELECT → NAME_INPUT
    """
    choice = text.strip().lower()
    language = LANG_MAP.get(choice)

    if not language:
        # Try to fuzzy-match common variants
        if "hindi" in choice or "हिंदी" in choice:
            language = "hi"
        elif "tamil" in choice or "தமிழ்" in choice:
            language = "ta"
        elif "english" in choice or "eng" in choice:
            language = "en"
        else:
            # Invalid — re-prompt
            await send_text(
                phone,
                "Kripya 1, 2, ya 3 mein se chunein:\n1. Hindi  2. Tamil  3. English"
            )
            return

    await update_user_data(phone, language=language)
    await send_text(phone, get_message("ask_name", language))
    await set_state(phone, ConversationState.NAME_INPUT)


async def _handle_name_input(phone: str, text: str) -> None:
    """
    NAME_INPUT — User sends store name
    Response: Ask for pin code
    Transition: NAME_INPUT → PINCODE
    """
    store_name = text.strip()
    if len(store_name) < 2:
        user_data = await get_user_data(phone)
        lang = user_data.get("language", "hi")
        await send_text(phone, get_message("ask_name", lang))
        return

    user_data = await update_user_data(phone, store_name=store_name)
    lang = user_data.get("language", "hi")
    await send_text(phone, get_message("ask_pincode", lang))
    await set_state(phone, ConversationState.PINCODE)


async def _handle_pincode(phone: str, text: str, db: Session) -> None:
    """
    PINCODE — User sends pin code
    Response: Confirm registration + sales tutorial
    Transition: PINCODE → ACTIVE
    Side effect: Creates Store record in PostgreSQL
    """
    pin_code = text.strip()

    # Basic validation — Indian pin codes are 6 digits
    cleaned = "".join(c for c in pin_code if c.isdigit())
    if len(cleaned) != 6:
        user_data = await get_user_data(phone)
        lang = user_data.get("language", "hi")
        msg = {
            "hi": "Kripya sahi 6-digit pin code bhejein.",
            "ta": "சரியான 6-digit pin code அனுப்புங்கள்.",
            "en": "Please send a valid 6-digit pin code.",
        }
        await send_text(phone, msg.get(lang, msg["hi"]))
        return

    user_data = await get_user_data(phone)
    lang = user_data.get("language", "hi")
    store_name = user_data.get("store_name", "My Store")

    # ── Create Store in DB ──
    existing = db.query(Store).filter(Store.whatsapp_number == phone).first()
    if not existing:
        store = Store(
            whatsapp_number=phone,
            name=store_name,
            pin_code=cleaned,
            language=lang,
        )
        db.add(store)
        db.commit()
        logger.info("Registered store '%s' for %s", store_name, phone)
    else:
        # Update existing store
        existing.name = store_name
        existing.pin_code = cleaned
        existing.language = lang
        db.commit()
        logger.info("Updated store '%s' for %s", store_name, phone)

    # Send confirmation + tutorial
    await send_text(
        phone,
        get_message("registration_done", lang, store_name=store_name),
    )
    await set_state(phone, ConversationState.ACTIVE)


async def _handle_active(phone: str, text: str, db: Session) -> None:
    """
    ACTIVE — User sends sales data
    Response: Parsed confirmation or error
    Transition: ACTIVE → AWAITING_CONFIRMATION
    """
    # Check for language switch commands
    lower = text.strip().lower()
    if _is_language_switch(lower):
        await _switch_language(phone, lower, db)
        return

    # Look up store and language
    store = db.query(Store).filter(Store.whatsapp_number == phone).first()
    lang = store.language if store else "hi"

    # Parse the sales message with Gemini
    parsed_items = await parse_sales_message(text, language=lang)

    if not parsed_items:
        await send_text(phone, get_message("parse_error", lang))
        return

    # Store pending items in Redis for confirmation
    await set_pending_items(phone, parsed_items)

    # Send confirmation message
    await send_confirmation(phone, parsed_items, language=lang)
    await set_state(phone, ConversationState.AWAITING_CONFIRMATION)


async def _handle_confirmation(phone: str, text: str, db: Session) -> None:
    """
    AWAITING_CONFIRMATION — User confirms or rejects parsed sales
    On confirm: persist to DB, return to ACTIVE
    On reject:  clear pending, return to ACTIVE
    """
    lower = text.strip().lower()

    store = db.query(Store).filter(Store.whatsapp_number == phone).first()
    lang = store.language if store else "hi"

    if lower in AFFIRMATIVES:
        # ── TASK 4: Persist confirmed sales ──
        pending = await get_pending_items(phone)
        if pending and store:
            persist_sales(db, store.store_id, pending, source="text")
            await send_text(phone, get_message("sales_saved", lang))
        else:
            await send_text(phone, get_message("parse_error", lang))

        await clear_pending_items(phone)
        await set_state(phone, ConversationState.ACTIVE)

    elif lower in NEGATIVES:
        await clear_pending_items(phone)
        await send_text(phone, get_message("sales_rejected", lang))
        await set_state(phone, ConversationState.ACTIVE)

    else:
        # Might be a new sales message — try parsing
        parsed_items = await parse_sales_message(text, language=lang)
        if parsed_items:
            # User sent new data instead of confirming
            await clear_pending_items(phone)
            await set_pending_items(phone, parsed_items)
            await send_confirmation(phone, parsed_items, language=lang)
            # Stay in AWAITING_CONFIRMATION
        else:
            # Unclear input — re-prompt
            confirm_msg = {
                "hi": "Kripya 'Haan' ya 'Nahi' mein jawab dein.",
                "ta": "'ஆமா' அல்லது 'இல்ல' என்று பதிலளிக்கவும்.",
                "en": "Please reply 'Yes' or 'No'.",
            }
            await send_text(phone, confirm_msg.get(lang, confirm_msg["hi"]))


# ════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════

def _extract_message(body: dict) -> tuple[Optional[str], Optional[str]]:
    """
    Extract phone number and message text from Meta webhook payload.

    Meta sends:
    {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543210",
                        "text": {"body": "Atta 5kg – 3"}
                    }]
                }
            }]
        }]
    }
    """
    try:
        entry = body.get("entry", [])
        if not entry:
            return None, None

        changes = entry[0].get("changes", [])
        if not changes:
            return None, None

        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None, None

        msg = messages[0]
        phone = msg.get("from")
        text = msg.get("text", {}).get("body", "").strip()

        if not phone or not text:
            return None, None

        return phone, text

    except (IndexError, KeyError, TypeError) as e:
        logger.warning("Failed to extract message from webhook payload: %s", e)
        return None, None


def _is_language_switch(text: str) -> bool:
    """Check if the user wants to switch language."""
    switch_triggers = [
        "hindi", "tamil", "english",
        "hindi mein baat karo", "tamil mein baat karo",
        "change language", "bhasha badlo",
        "हिंदी", "தமிழ்",
    ]
    return any(trigger in text for trigger in switch_triggers)


async def _switch_language(phone: str, text: str, db: Session) -> None:
    """Handle runtime language switching."""
    if "hindi" in text or "हिंदी" in text:
        new_lang = "hi"
    elif "tamil" in text or "தமிழ்" in text:
        new_lang = "ta"
    elif "english" in text:
        new_lang = "en"
    else:
        return

    # Update in DB
    store = db.query(Store).filter(Store.whatsapp_number == phone).first()
    if store:
        store.language = new_lang
        db.commit()

    # Update in Redis session
    await update_user_data(phone, language=new_lang)

    confirmations = {
        "hi": "Bhasha Hindi mein set ho gayi. ✅",
        "ta": "மொழி Tamil-ல் set ஆகிவிட்டது. ✅",
        "en": "Language set to English. ✅",
    }
    await send_text(phone, confirmations[new_lang])
