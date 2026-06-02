from collections.abc import Callable
from typing import Literal

from goni.config import DEFAULT_VISION_PROVIDER
from goni.decide.brain_gemini import ask_gemini_vision
from goni.decide.brain_grok import ask_grok_vision
from goni.decide.brain_local import ask_local_vision_placeholder
from goni.decide.vision_payload import PreparedVisionPayload, prepare_vision_payload


VisionProvider = Literal["auto", "gemini", "grok", "local"]
ProviderCallable = Callable[[PreparedVisionPayload], dict]
GrokCallable = Callable[..., dict]


def answer_screen_question(
    user_question: str,
    perception: dict,
    *,
    provider: VisionProvider = "auto",
    gemini_client: ProviderCallable = ask_gemini_vision,
    grok_client: GrokCallable = ask_grok_vision,
    local_client: ProviderCallable = ask_local_vision_placeholder,
) -> dict:
    payload = prepare_vision_payload(user_question, perception)
    selected_provider = _resolve_provider(provider)

    if selected_provider == "local":
        return local_client(payload)

    if selected_provider == "grok":
        return grok_client(payload, route_reason="explicit_grok")

    gemini_result = gemini_client(payload)
    if _should_fallback_to_grok(gemini_result):
        return grok_client(payload, route_reason="gemini_fallback")

    return gemini_result


def _resolve_provider(provider: VisionProvider) -> Literal["gemini", "grok", "local"]:
    if provider != "auto":
        return provider

    if DEFAULT_VISION_PROVIDER in {"gemini", "grok", "local"}:
        return DEFAULT_VISION_PROVIDER

    return "gemini"


def _should_fallback_to_grok(result: dict) -> bool:
    if not result.get("fallback_recommended"):
        return False

    route_reason = result.get("route_reason", "")
    if route_reason.startswith("provider_unavailable:missing_api_key"):
        return False

    return True
