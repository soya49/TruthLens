from app.config import settings


def provider_status() -> dict[str, str | bool]:
    enabled = bool(settings.ai_api_key and settings.ai_provider.lower() != "none")
    return {"provider": settings.ai_provider, "enabled": enabled, "mode": "provider" if enabled else "demo"}


def enrich_with_provider(_payload: dict) -> dict:
    """Provider seam: external calls are intentionally opt-in and never fabricate demo findings."""
    return {"status": provider_status(), "message": "No external AI provider configured; deterministic analysis was used."}
