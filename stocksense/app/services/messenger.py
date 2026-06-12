"""
Messenger Service — TASK 2
Wraps the WhatsApp Business Cloud API for sending messages.

Provides:
  - send_text(to, body)              → plain text message
  - send_confirmation(to, parsed_items, language) → formatted confirmation
"""

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GRAPH_API_URL = (
    f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
)


def _has_real_whatsapp_credentials() -> bool:
    """Return True only when the WhatsApp credentials look production-ready."""
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
        return False

    placeholder_values = {"test_token", "test_phone_id"}
    if (
        settings.WHATSAPP_TOKEN in placeholder_values
        or settings.WHATSAPP_PHONE_ID in placeholder_values
    ):
        return False

    return True


# ── Multi-language message templates (PRD §7 user flow) ──
MESSAGES = {
    # ── Onboarding: Language selection (Step 2) ──
    "welcome": {
        "hi": (
            "Namaste! 🙏 StockSense aapki dukaan ke liye smart stock suggestions deta hai.\n"
            "Aap kaunsi bhasha mein baat karna chahenge?\n"
            "1. Hindi  2. Tamil  3. English"
        ),
        "ta": (
            "வணக்கம்! 🙏 StockSense உங்கள் கடைக்கு smart stock suggestions தருகிறது.\n"
            "நீங்கள் எந்த மொழியில் பேச விரும்புகிறீர்கள்?\n"
            "1. Hindi  2. Tamil  3. English"
        ),
        "en": (
            "Namaste! 🙏 StockSense gives smart stock suggestions for your store.\n"
            "Which language would you like to chat in?\n"
            "1. Hindi  2. Tamil  3. English"
        ),
    },
    # ── Onboarding: Ask store name (Step 3a) ──
    "ask_name": {
        "hi": "Aapki dukaan ka naam kya hai?",
        "ta": "உங்கள் கடையின் பெயர் என்ன?",
        "en": "What is your store name?",
    },
    # ── Onboarding: Ask pin code (Step 3b) ──
    "ask_pincode": {
        "hi": "Aapka pin code kya hai?",
        "ta": "உங்கள் pin code என்ன?",
        "en": "What is your pin code?",
    },
    # ── Onboarding: Registration confirmed (Step 3c + 4) ──
    "registration_done": {
        "hi": (
            "Perfect! {store_name} register ho gaya. ✅\n"
            "Ab main aapko sikhaunga ki sales kaise share karein.\n\n"
            "Rozana raat ko apni sales aise bhejein:\n"
            "[Item naam] – [bikne wali quantity]\n"
            "Example: Atta 5kg – 3, Maggi – 12, Parle-G – 20"
        ),
        "ta": (
            "Perfect! {store_name} register ஆகிவிட்டது. ✅\n"
            "இப்போது sales share செய்வது எப்படி என்று கற்றுக்கொள்வோம்.\n\n"
            "தினமும் இரவு உங்கள் sales இப்படி அனுப்புங்கள்:\n"
            "[பொருள் பெயர்] – [விற்ற அளவு]\n"
            "Example: Atta 5kg – 3, Maggi – 12, Parle-G – 20"
        ),
        "en": (
            "Perfect! {store_name} has been registered. ✅\n"
            "Now let me show you how to share your sales.\n\n"
            "Send your daily sales like this:\n"
            "[Item name] – [quantity sold]\n"
            "Example: Atta 5kg – 3, Maggi – 12, Parle-G – 20"
        ),
    },
    # ── Sales confirmation prompt (Step 5) ──
    "confirm_prompt": {
        "hi": "Sahi hai? Haan / Nahi",
        "ta": "சரியா? ஆமா / இல்ல",
        "en": "Is this correct? Yes / No",
    },
    # ── Sales saved acknowledgement ──
    "sales_saved": {
        "hi": "Saved! ✅ Kal phir bhejein. Jitna zyada data, utna better forecast. 📊",
        "ta": "Save ஆகிவிட்டது! ✅ நாளையும் அனுப்புங்கள். அதிக data, சிறந்த forecast. 📊",
        "en": "Saved! ✅ Send again tomorrow. More data means better forecasts. 📊",
    },
    # ── Sales rejected — ask to resend ──
    "sales_rejected": {
        "hi": "Koi baat nahi! Apni sales dubara bhejein. 🔄",
        "ta": "பரவாயில்லை! உங்கள் sales மீண்டும் அனுப்புங்கள். 🔄",
        "en": "No problem! Please resend your sales data. 🔄",
    },
    # ── Parse failure ──
    "parse_error": {
        "hi": (
            "Maaf kijiye, main samajh nahi paaya. 😅\n"
            "Kripya aise bhejein: Atta 5kg – 3, Maggi – 12"
        ),
        "ta": (
            "மன்னிக்கவும், புரியவில்லை. 😅\n"
            "இப்படி அனுப்புங்கள்: Atta 5kg – 3, Maggi – 12"
        ),
        "en": (
            "Sorry, I couldn't understand that. 😅\n"
            "Please send like this: Atta 5kg – 3, Maggi – 12"
        ),
    },
}


def get_message(key: str, language: str = "hi", **kwargs) -> str:
    """
    Retrieve a localised message template.
    Falls back to Hindi, then English if the key/language is missing.
    """
    templates = MESSAGES.get(key, {})
    text = templates.get(language) or templates.get(
        "hi") or templates.get("en", "")
    if kwargs:
        text = text.format(**kwargs)
    return text


async def send_text(to: str, body: str) -> dict:
    """
    Send a plain-text WhatsApp message via Meta Cloud API.

    Args:
        to:   Recipient phone number with country code (e.g. "919876543210")
        body: Plain-text message body

    Returns:
        Meta API response dict, or error dict on failure.
    """
    if not _has_real_whatsapp_credentials():
        logger.warning(
            "WhatsApp credentials not configured for local dev — message not sent to %s. Mock send: %s",
            to,
            body,
        )
        print(f"[WhatsApp mock send to {to}] {body}")
        return {"status": "skipped", "reason": "credentials_not_configured"}

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GRAPH_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            logger.info("Message sent to %s (id=%s)", to,
                        data.get("messages", [{}])[0].get("id"))
            return data
    except httpx.HTTPStatusError as e:
        logger.error("WhatsApp API HTTP error %s: %s",
                     e.response.status_code, e.response.text)
        return {"status": "error", "code": e.response.status_code, "detail": e.response.text}
    except Exception as e:
        logger.error("WhatsApp send failed: %s", e, exc_info=True)
        return {"status": "error", "detail": str(e)}


async def send_confirmation(
    to: str,
    parsed_items: list[dict],
    language: str = "hi",
) -> dict:
    """
    Format and send a sales confirmation message.

    PRD §7 format:
        "Maine yeh record kiya:
         ✅ Atta 5kg → 3 bags
         ✅ Maggi 70g → 12 packets
         Sahi hai? Haan / Nahi"

    Args:
        to:            Recipient phone number
        parsed_items:  Output from nlp_parser.parse_sales_message
        language:      User's preferred language code

    Returns:
        Meta API response dict
    """
    header = {
        "hi": "Maine yeh record kiya:",
        "ta": "நான் இதை record செய்தேன்:",
        "en": "I recorded the following:",
    }

    lines = [header.get(language, header["hi"])]

    for item in parsed_items:
        unit = item.get("unit") or "units"
        flag = " ⚠️" if item.get("needs_confirmation") else ""
        lines.append(f"✅ {item['sku_name']} → {item['quantity']} {unit}{flag}")

    lines.append("")
    lines.append(get_message("confirm_prompt", language))

    body = "\n".join(lines)
    return await send_text(to, body)
