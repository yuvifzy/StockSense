"""
Conversation state manager — Redis-backed state machine for WhatsApp onboarding.

States: NEW → LANG_SELECT → NAME_INPUT → PINCODE → CONFIRMED → ACTIVE

Also handles the AWAITING_CONFIRMATION sub-state during sales flow,
and stores pending parsed items for confirmation.
"""

import json
import logging
from enum import Enum
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# ── Redis connection ──
_redis: Optional[aioredis.Redis] = None

STATE_PREFIX = "ss:state:"          # ss:state:{phone} → state string
DATA_PREFIX = "ss:data:"            # ss:data:{phone}  → JSON blob (store name, etc.)
PENDING_PREFIX = "ss:pending:"      # ss:pending:{phone} → JSON (parsed items awaiting confirm)
STATE_TTL = 60 * 60 * 24 * 30       # 30 days


class ConversationState(str, Enum):
    NEW = "NEW"
    LANG_SELECT = "LANG_SELECT"
    NAME_INPUT = "NAME_INPUT"
    PINCODE = "PINCODE"
    CONFIRMED = "CONFIRMED"
    ACTIVE = "ACTIVE"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"


async def get_redis() -> aioredis.Redis:
    """Lazy-init async Redis connection using centralised settings."""
    global _redis
    if _redis is None:
        logger.info("Connecting to Redis: %s", settings.REDIS_URL[:30] + "...")
        _redis = aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
    return _redis


async def get_state(phone: str) -> str:
    """Get the conversation state for a phone number. Defaults to NEW."""
    r = await get_redis()
    state = await r.get(f"{STATE_PREFIX}{phone}")
    return state or ConversationState.NEW


async def set_state(phone: str, state: str) -> None:
    """Set the conversation state for a phone number."""
    r = await get_redis()
    await r.set(f"{STATE_PREFIX}{phone}", state, ex=STATE_TTL)
    logger.info("State %s → %s for %s", "?", state, phone)


async def get_user_data(phone: str) -> dict:
    """Get temporary onboarding data stored during the flow."""
    r = await get_redis()
    raw = await r.get(f"{DATA_PREFIX}{phone}")
    if raw:
        return json.loads(raw)
    return {}


async def set_user_data(phone: str, data: dict) -> None:
    """Store temporary onboarding data."""
    r = await get_redis()
    await r.set(f"{DATA_PREFIX}{phone}", json.dumps(data), ex=STATE_TTL)


async def update_user_data(phone: str, **kwargs) -> dict:
    """Merge new fields into the user's temporary data."""
    data = await get_user_data(phone)
    data.update(kwargs)
    await set_user_data(phone, data)
    return data


async def set_pending_items(phone: str, items: list[dict]) -> None:
    """Store parsed sales items pending user confirmation."""
    r = await get_redis()
    await r.set(f"{PENDING_PREFIX}{phone}", json.dumps(items), ex=60 * 60)  # 1h TTL


async def get_pending_items(phone: str) -> list[dict]:
    """Retrieve pending sales items for confirmation."""
    r = await get_redis()
    raw = await r.get(f"{PENDING_PREFIX}{phone}")
    if raw:
        return json.loads(raw)
    return []


async def clear_pending_items(phone: str) -> None:
    """Clear pending items after confirmation or rejection."""
    r = await get_redis()
    await r.delete(f"{PENDING_PREFIX}{phone}")


async def clear_user_session(phone: str) -> None:
    """Wipe all session data for a phone number (full reset)."""
    r = await get_redis()
    await r.delete(
        f"{STATE_PREFIX}{phone}",
        f"{DATA_PREFIX}{phone}",
        f"{PENDING_PREFIX}{phone}",
    )
