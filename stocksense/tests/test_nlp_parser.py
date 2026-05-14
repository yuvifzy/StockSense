"""
Tests for nlp_parser.py — 10 sample messages from PRD context.

Tests use mocked Gemini responses so they can run without an API key.
Each test covers a distinct input style from the kirana store context:
  1. Standard Hindi format (PRD §7 example)
  2. Hinglish with "bika" / "biki"
  3. English structured
  4. Voice-transcript messy style
  5. Single item
  6. Hindi with units
  7. Mixed Hindi-English (Hinglish)
  8. Comma-separated terse
  9. Ambiguous / low-confidence input
  10. Empty / no-sales message
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# We test the core parsing logic — mock Gemini so tests run offline
from app.services.nlp_parser import parse_sales_message, _safe_int, format_parsed_items_for_log


# ──────────────────────────────────────────────────
# Helper: build a mock Gemini response
# ──────────────────────────────────────────────────
def _mock_gemini_response(json_data: list[dict]) -> MagicMock:
    """Create a mock response object that mimics generate_content response."""
    mock = MagicMock()
    mock.text = json.dumps(json_data)
    return mock


def _patch_client(response_mock):
    """
    Create a patch context for app.services.nlp_parser._get_client
    that returns a mock client with client.aio.models.generate_content → response_mock.
    """
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=response_mock)
    return patch("app.services.nlp_parser._get_client", return_value=mock_client)


# ──────────────────────────────────────────────────
# Test 1: Standard PRD §7 example
# "Atta 5kg – 3, Maggi – 12, Parle-G – 20, Tata Salt – 5"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_prd_example_standard():
    gemini_output = [
        {"sku_name": "Atta 5kg", "quantity": 3, "unit": "bags", "confidence": 0.95},
        {"sku_name": "Maggi", "quantity": 12, "unit": "packets", "confidence": 0.92},
        {"sku_name": "Parle-G", "quantity": 20, "unit": "packets", "confidence": 0.93},
        {"sku_name": "Tata Salt", "quantity": 5, "unit": "packets", "confidence": 0.90},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message(
            "Atta 5kg – 3, Maggi – 12, Parle-G – 20, Tata Salt – 5", "hi"
        )

    assert len(result) == 4
    assert result[0]["sku_name"] == "Atta 5kg"
    assert result[0]["quantity"] == 3
    assert result[0]["unit"] == "bags"
    assert result[0]["needs_confirmation"] is False


# ──────────────────────────────────────────────────
# Test 2: Hinglish with "bika" / "biki"
# "atta 5kg – 3 bika, maggi – 12 biki"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_hinglish_bika_biki():
    gemini_output = [
        {"sku_name": "Atta 5kg", "quantity": 3, "unit": "bags", "confidence": 0.88},
        {"sku_name": "Maggi", "quantity": 12, "unit": "packets", "confidence": 0.85},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message("atta 5kg – 3 bika, maggi – 12 biki", "hi")

    assert len(result) == 2
    assert result[0]["quantity"] == 3
    assert result[1]["quantity"] == 12
    # Both above 0.7, so no confirmation needed
    assert all(not item["needs_confirmation"] for item in result)


# ──────────────────────────────────────────────────
# Test 3: English structured
# "Sold 5 Toor Dal 1kg, 10 Sugar 5kg, 3 Rice 25kg"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_english_structured():
    gemini_output = [
        {"sku_name": "Toor Dal 1kg", "quantity": 5, "unit": "packets", "confidence": 0.92},
        {"sku_name": "Sugar 5kg", "quantity": 10, "unit": "bags", "confidence": 0.90},
        {"sku_name": "Rice 25kg", "quantity": 3, "unit": "bags", "confidence": 0.91},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message(
            "Sold 5 Toor Dal 1kg, 10 Sugar 5kg, 3 Rice 25kg", "en"
        )

    assert len(result) == 3
    assert result[0]["sku_name"] == "Toor Dal 1kg"
    assert result[1]["quantity"] == 10


# ──────────────────────────────────────────────────
# Test 4: Voice-transcript messy style
# "sold 3 toor dal 2 maggi aur 5 namak"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_voice_transcript_messy():
    gemini_output_str = '[{"sku_name": "Toor Dal", "quantity": 3, "unit": null, "confidence": 0.75}, {"sku_name": "Maggi", "quantity": 2, "unit": "packets", "confidence": 0.80}, {"sku_name": "Namak", "quantity": 5, "unit": null, "confidence": 0.72}]'

    mock_resp = MagicMock()
    mock_resp.text = gemini_output_str
    with _patch_client(mock_resp):
        result = await parse_sales_message(
            "sold 3 toor dal 2 maggi aur 5 namak", "hi"
        )

    assert len(result) == 3
    assert result[0]["unit"] is None
    assert result[2]["sku_name"] == "Namak"


# ──────────────────────────────────────────────────
# Test 5: Single item
# "Maggi – 12"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_single_item():
    gemini_output = [
        {"sku_name": "Maggi", "quantity": 12, "unit": "packets", "confidence": 0.95},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message("Maggi – 12", "hi")

    assert len(result) == 1
    assert result[0]["sku_name"] == "Maggi"
    assert result[0]["quantity"] == 12


# ──────────────────────────────────────────────────
# Test 6: Hindi with units
# "Aashirvaad atta 10 bori, tel 5 litre, cheeni 8 kilo"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_hindi_with_units():
    gemini_output_str = json.dumps([
        {"sku_name": "Aashirvaad Atta", "quantity": 10, "unit": "bori", "confidence": 0.88},
        {"sku_name": "Tel", "quantity": 5, "unit": "litre", "confidence": 0.82},
        {"sku_name": "Cheeni", "quantity": 8, "unit": "kg", "confidence": 0.85},
    ])

    mock_resp = MagicMock()
    mock_resp.text = gemini_output_str
    with _patch_client(mock_resp):
        result = await parse_sales_message(
            "Aashirvaad atta 10 bori, tel 5 litre, cheeni 8 kilo", "hi"
        )

    assert len(result) == 3
    assert result[0]["unit"] == "bori"
    assert result[2]["sku_name"] == "Cheeni"


# ──────────────────────────────────────────────────
# Test 7: Mixed Hindi-English (Hinglish)
# "Today 5 Parle-G biki, 3 packet doodh, Surf Excel 2"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_mixed_hinglish():
    gemini_output = [
        {"sku_name": "Parle-G", "quantity": 5, "unit": "packets", "confidence": 0.88},
        {"sku_name": "Doodh", "quantity": 3, "unit": "packets", "confidence": 0.80},
        {"sku_name": "Surf Excel", "quantity": 2, "unit": None, "confidence": 0.85},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message(
            "Today 5 Parle-G biki, 3 packet doodh, Surf Excel 2", "hi"
        )

    assert len(result) == 3
    assert result[2]["unit"] is None


# ──────────────────────────────────────────────────
# Test 8: Comma-separated terse
# "Maggi 15, Biscuit 20, Oil 3, Dal 4"
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_comma_separated_terse():
    gemini_output = [
        {"sku_name": "Maggi", "quantity": 15, "unit": "packets", "confidence": 0.90},
        {"sku_name": "Biscuit", "quantity": 20, "unit": "packets", "confidence": 0.88},
        {"sku_name": "Oil", "quantity": 3, "unit": "bottles", "confidence": 0.82},
        {"sku_name": "Dal", "quantity": 4, "unit": "kg", "confidence": 0.80},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message("Maggi 15, Biscuit 20, Oil 3, Dal 4", "en")

    assert len(result) == 4
    assert result[0]["quantity"] == 15


# ──────────────────────────────────────────────────
# Test 9: Ambiguous / low-confidence → needs_confirmation
# "kuch saamaan becha 200 ka" (unclear: 200 could be price, not quantity)
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_ambiguous_low_confidence():
    gemini_output = [
        {"sku_name": "Saamaan", "quantity": 200, "unit": None, "confidence": 0.4},
    ]

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message("kuch saamaan becha 200 ka", "hi")

    assert len(result) == 1
    assert result[0]["needs_confirmation"] is True
    assert result[0]["confidence"] < 0.7


# ──────────────────────────────────────────────────
# Test 10: Empty / no-sales message
# "Aaj dukaan band thi" (shop was closed today — no sales)
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_empty_no_sales():
    gemini_output = []  # Gemini returns empty array

    with _patch_client(_mock_gemini_response(gemini_output)):
        result = await parse_sales_message("Aaj dukaan band thi", "hi")

    assert result == []


# ──────────────────────────────────────────────────
# Test: Empty string input (no Gemini call needed)
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_empty_string_input():
    result = await parse_sales_message("", "en")
    assert result == []

    result = await parse_sales_message("   ", "en")
    assert result == []


# ──────────────────────────────────────────────────
# Test: Gemini returns invalid JSON
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_gemini_returns_invalid_json():
    mock_resp = MagicMock()
    mock_resp.text = "This is not JSON at all"
    with _patch_client(mock_resp):
        result = await parse_sales_message("some message", "en")

    assert result == []


# ──────────────────────────────────────────────────
# Test: Gemini returns JSON wrapped in markdown fences
# ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_gemini_markdown_fenced_json():
    items = [{"sku_name": "Rice", "quantity": 5, "unit": "kg", "confidence": 0.9}]

    mock_resp = MagicMock()
    mock_resp.text = f"```json\n{json.dumps(items)}\n```"
    with _patch_client(mock_resp):
        result = await parse_sales_message("Rice 5 kg becha", "hi")

    assert len(result) == 1
    assert result[0]["sku_name"] == "Rice"


# ──────────────────────────────────────────────────
# Test: _safe_int utility
# ──────────────────────────────────────────────────
def test_safe_int():
    assert _safe_int(5) == 5
    assert _safe_int("10") == 10
    assert _safe_int(0) == 1      # min 1
    assert _safe_int(-3) == 1     # min 1
    assert _safe_int("abc") == 1  # fallback
    assert _safe_int(None) == 1   # fallback


# ──────────────────────────────────────────────────
# Test: format_parsed_items_for_log
# ──────────────────────────────────────────────────
def test_format_parsed_items():
    items = [
        {"sku_name": "Atta", "quantity": 3, "unit": "bags", "confidence": 0.9, "needs_confirmation": False},
        {"sku_name": "Dal", "quantity": 2, "unit": None, "confidence": 0.5, "needs_confirmation": True},
    ]
    output = format_parsed_items_for_log(items)
    assert "Atta" in output
    assert "⚠️" in output  # Dal has needs_confirmation
    assert format_parsed_items_for_log([]) == "(no items parsed)"
