"""
NLP Parser Service — TASK 1
Parses free-text / Hindi / Hinglish / Tamil sales messages into structured
SKU + quantity records using Gemini 1.5 Flash.

Input:  raw WhatsApp message string
Output: list of { sku_name, quantity, unit, needs_confirmation }
"""

import json
import logging
from typing import Optional

from google import genai

from app.config import settings

logger = logging.getLogger(__name__)

# ── Gemini client (lazy-init to avoid crash when API key is empty) ──
_client = None
MODEL_NAME = "gemini-2.0-flash-lite"


def _get_client() -> genai.Client:
    """Lazy-init Gemini client on first use."""
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


# ── System prompt for structured extraction ──
EXTRACTION_PROMPT = """You are a sales data extraction assistant for Indian kirana (grocery) stores.

Your job: extract EVERY item and its sold quantity from the user's message.

RULES:
1. The message may be in Hindi, Hinglish (Hindi-English mix), Tamil, or English.
2. Common kirana terms: "bika/biki/becha" = sold, "packet/pkt" = packets, "bag" = bags.
3. Extract the SKU name exactly as the user wrote it (preserve Hindi/English).
4. Extract the quantity as an integer. If no quantity is given, default to 1.
5. Extract the unit if mentioned (bags, packets, kg, litre, etc). If not mentioned, set to null.
6. For each item, assign a confidence score between 0.0 and 1.0:
   - 1.0 = clearly stated item + quantity
   - 0.7–0.9 = minor ambiguity (e.g. unit unclear)
   - < 0.7 = significant ambiguity (e.g. unclear if it's a quantity or price)

RESPOND ONLY with a valid JSON array. No markdown, no explanation. Example:
[
  {"sku_name": "Atta 5kg", "quantity": 3, "unit": "bags", "confidence": 0.95},
  {"sku_name": "Maggi", "quantity": 12, "unit": "packets", "confidence": 0.9},
  {"sku_name": "Toor Dal", "quantity": 2, "unit": null, "confidence": 0.6}
]

If the message contains NO sales data at all, return an empty array: []
"""


async def parse_sales_message(
    raw_text: str, language: str = "en"
) -> list[dict]:
    """
    Parse a natural-language sales message into structured data using Gemini Flash.

    Args:
        raw_text:  Raw WhatsApp message text
                   e.g. "Atta 5kg – 3 bika, Maggi – 12"
        language:  User's preferred language code (en, hi, ta)

    Returns:
        List of dicts:
        [
            {
                "sku_name": str,
                "quantity": int,
                "unit": str | None,
                "confidence": float,
                "needs_confirmation": bool
            },
            ...
        ]

    On failure returns an empty list and logs the error.
    """
    if not raw_text or not raw_text.strip():
        return []

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.strip() == "test-key":
        logger.warning(
            "GEMINI_API_KEY is missing or set to 'test-key'; returning mock parsed sales response for local development."
        )
        return [{
            "sku_name": "Test Item",
            "quantity": 1,
            "unit": "units",
            "confidence": 0.9,
            "needs_confirmation": False,
        }]

    try:
        prompt = (
            f"{EXTRACTION_PROMPT}\n\n"
            f"User language preference: {language}\n"
            f"User message:\n\"{raw_text}\""
        )

        response = await _get_client().aio.models.generate_content(
            model=MODEL_NAME, contents=prompt
        )

        # Extract text from the response
        response_text = response.text.strip()

        # Strip markdown code fences if Gemini wraps the JSON
        if response_text.startswith("```"):
            # Remove ```json ... ``` or ``` ... ```
            lines = response_text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            response_text = "\n".join(lines).strip()

        parsed_items = json.loads(response_text)

        if not isinstance(parsed_items, list):
            logger.warning(
                "Gemini returned non-list response: %s", response_text)
            return []

        # Normalise each item and flag low-confidence items
        result = []
        for item in parsed_items:
            normalised = {
                "sku_name": str(item.get("sku_name", "")).strip(),
                "quantity": _safe_int(item.get("quantity", 1)),
                "unit": item.get("unit") or None,
                "confidence": float(item.get("confidence", 0.5)),
                "needs_confirmation": False,
            }
            # Flag if confidence is below threshold
            if normalised["confidence"] < 0.7:
                normalised["needs_confirmation"] = True

            # Skip items with empty names
            if not normalised["sku_name"]:
                continue

            result.append(normalised)

        logger.info(
            "Parsed %d items from message (lang=%s): %s",
            len(result), language, raw_text[:80],
        )
        return result

    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini JSON response: %s", e)
        return []
    except Exception as e:
        logger.error("NLP parser error: %s", e, exc_info=True)
        return []


def _safe_int(value) -> int:
    """Convert a value to int, defaulting to 1 on failure."""
    try:
        return max(1, int(value))
    except (ValueError, TypeError):
        return 1


def format_parsed_items_for_log(items: list[dict]) -> str:
    """
    Format parsed items into a human-readable string for debugging.
    """
    if not items:
        return "(no items parsed)"
    lines = []
    for item in items:
        flag = " ⚠️" if item.get("needs_confirmation") else ""
        unit = item.get("unit") or "units"
        lines.append(
            f"  {item['sku_name']} → {item['quantity']} {unit} "
            f"(conf: {item.get('confidence', '?')}){flag}"
        )
    return "\n".join(lines)
