import httpx
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

LITELLM_MODEL_LIST = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

PROVIDER_MAP = {
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "gemini": "Google Gemini",
    "groq": "Groq",
}

PROVIDER_ALIASES = {
    "google": "gemini",
    "google_ai": "gemini",
    "googleai": "gemini",
    "vertex_ai": "gemini",
    "groqai": "groq",
    "groq_ai": "groq",
}

PROVIDER_MODEL_EXCLUDES = {
    "gemini": {"gemma", "lyria"},
    "groq": set(),
}

TEXT_MODES = {
    "chat",
    "completion",
    "text",
    "text_completion",
    "responses",
}

NON_TEXT_KEYWORDS = {
    "embedding",
    "embed",
    "image",
    "audio",
    "speech",
    "transcribe",
    "whisper",
    "tts",
    "rerank",
    "re-rank",
    "moderation",
}


async def fetch_litellm_models() -> dict:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(LITELLM_MODEL_LIST)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.exception("Failed to fetch LiteLLM model catalog")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to fetch model catalog",
        ) from exc


def build_provider_seed(model_catalog: dict) -> list[dict]:
    grouped: dict[str, list[tuple[str, dict]]] = {}

    for model_key, model_data in model_catalog.items():
        if "sample_spec" in model_key:
            continue

        if model_key.count("/") > 1:
            # Skip multi-segment keys like "gemini/xai/grok-4.1" to avoid cross-provider pollution.
            continue

        if not _is_text_generation_model(model_key, model_data):
            continue

        prefix = _resolve_provider_prefix(model_key, model_data)
        if prefix in PROVIDER_ALIASES:
            prefix = PROVIDER_ALIASES[prefix]

        if prefix not in PROVIDER_MAP:
            continue

        model_id = model_key.split("/", 1)[-1]
        if _is_excluded_provider_model(prefix, model_id):
            continue

        grouped.setdefault(prefix, []).append((model_id, model_data))

    provider_payload: list[dict] = []
    for slug, models in grouped.items():
        model_entries: list[dict] = []
        for model_id, _ in models:
            display_name = model_id.replace("-", " ").replace("_", " ").title()
            model_entries.append({"model_id": model_id, "display_name": display_name})

        provider_payload.append(
            {
                "slug": slug,
                "display_name": PROVIDER_MAP[slug],
                "models": model_entries,
            }
        )

    return provider_payload


def _resolve_provider_prefix(model_key: str, model_data: dict) -> str:
    provider = _get_provider_from_metadata(model_data)
    if provider:
        return provider

    if "/" in model_key:
        return model_key.split("/", 1)[0]

    return "openai"


def _get_provider_from_metadata(model_data: dict) -> str | None:
    if not isinstance(model_data, dict):
        return None

    for key in ("litellm_provider", "provider", "custom_llm_provider", "model_provider"):
        value = model_data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()

    return None


def _is_text_generation_model(model_key: str, model_data: dict) -> bool:
    if isinstance(model_data, dict):
        mode = model_data.get("mode") or model_data.get("model_mode") or model_data.get("task")
        if isinstance(mode, str) and mode.strip():
            normalized = mode.strip().lower().replace("-", "_")
            return normalized in TEXT_MODES

    lowered_key = model_key.lower()
    return not any(keyword in lowered_key for keyword in NON_TEXT_KEYWORDS)


def _is_excluded_provider_model(provider_slug: str, model_id: str) -> bool:
    exclusions = PROVIDER_MODEL_EXCLUDES.get(provider_slug, set())
    lowered = model_id.lower()
    return any(token in lowered for token in exclusions)
