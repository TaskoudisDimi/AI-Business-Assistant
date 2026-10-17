"""Claude API access shared by the AI features. Everything here is a no-op until
ANTHROPIC_API_KEY is set; routes check `enabled()` and return 503 otherwise."""
from datetime import datetime, timezone

import anthropic
from fastapi import HTTPException

from core.config import AI_DAILY_LIMIT, AI_MODEL, ANTHROPIC_API_KEY
from db.supabase_client import supabase

# Models that accept the server-side refusal fallback ("default" routing)
_FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}

_client: anthropic.Anthropic | None = None


def enabled() -> bool:
    return bool(ANTHROPIC_API_KEY)


def client() -> anthropic.Anthropic:
    global _client
    if not enabled():
        raise HTTPException(503, "AI features are not configured on this server")
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def request_options() -> dict:
    """Model plus refusal fallback: if a safety classifier declines, the API retries on
    a fallback model inside the same call instead of failing the request."""
    opts: dict = {"model": AI_MODEL}
    if AI_MODEL in _FALLBACK_MODELS:
        opts.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    return opts


def remaining_today(business_id: str) -> int:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    used = supabase.table("ai_requests").select("id", count="exact") \
        .eq("business_id", business_id).gte("created_at", start.isoformat()).execute().count or 0
    return max(AI_DAILY_LIMIT - used, 0)


def consume_quota(business_id: str, kind: str) -> None:
    if remaining_today(business_id) <= 0:
        raise HTTPException(429, "Daily AI limit reached for this business")
    supabase.table("ai_requests").insert({"business_id": business_id, "kind": kind}).execute()


def raise_for_api_error(e: Exception) -> None:
    """Map SDK errors to HTTP responses the frontend can show."""
    if isinstance(e, anthropic.RateLimitError):
        raise HTTPException(429, "The AI service is busy, try again in a minute")
    if isinstance(e, anthropic.BadRequestError):
        raise HTTPException(400, f"The AI service rejected the request: {e.message}")
    if isinstance(e, anthropic.AuthenticationError):
        raise HTTPException(503, "AI is misconfigured on the server (invalid API key)")
    if isinstance(e, anthropic.APIStatusError):
        raise HTTPException(502, "The AI service had an error, try again")
    if isinstance(e, anthropic.APIConnectionError):
        raise HTTPException(502, "Could not reach the AI service")
    raise e


def text_of(message) -> str:
    return "".join(b.text for b in message.content if b.type == "text").strip()
