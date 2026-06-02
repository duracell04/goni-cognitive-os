from __future__ import annotations

import json
from urllib import error, request

from goni.config import GROK_MODEL, XAI_API_KEY, XAI_BASE_URL
from goni.decide.vision_payload import PreparedVisionPayload, build_screen_prompt


def ask_grok_vision(payload: PreparedVisionPayload, *, route_reason: str = "explicit_grok") -> dict:
    if not XAI_API_KEY:
        return _unavailable(payload, "missing_api_key", route_reason)

    content = [{"type": "input_text", "text": build_screen_prompt(payload)}]
    if payload.image_data_url:
        content.insert(
            0,
            {
                "type": "input_image",
                "image_url": payload.image_data_url,
                "detail": "high",
            },
        )

    body = {
        "model": GROK_MODEL,
        "input": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "store": False,
    }
    url = f"{XAI_BASE_URL.rstrip('/')}/responses"

    try:
        data = _post_json(url, body)
        answer = _extract_answer(data)
    except Exception as exc:
        return {
            **_base_response(payload),
            "provider": "grok_unavailable",
            "answer": "Grok request failed.",
            "route_reason": "provider_error",
            "error": str(exc),
            "model": GROK_MODEL,
        }

    return {
        **_base_response(payload),
        "provider": "grok",
        "answer": answer,
        "route_reason": route_reason,
        "model": GROK_MODEL,
    }


def _post_json(url: str, body: dict) -> dict:
    encoded = json.dumps(body).encode("utf-8")
    req = request.Request(
        url,
        data=encoded,
        headers={
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def _extract_answer(data: dict) -> str:
    if "output_text" in data:
        return str(data["output_text"]).strip()

    output = data.get("output") or []
    text_parts = []
    for item in output:
        for content in item.get("content", []) or []:
            text = content.get("text")
            if text:
                text_parts.append(text)
    return "\n".join(text_parts).strip()


def _base_response(payload: PreparedVisionPayload) -> dict:
    return {
        "user_question": payload.user_question,
        "screenshot_path": payload.screenshot_path,
        "ocr_context_preview": payload.ocr_text[:1000],
        "ui_elements": payload.ui_elements[:10],
    }


def _unavailable(payload: PreparedVisionPayload, reason: str, route_reason: str) -> dict:
    return {
        **_base_response(payload),
        "provider": "grok_unavailable",
        "answer": "Grok is not configured. Set XAI_API_KEY to enable reasoning fallback.",
        "route_reason": f"provider_unavailable:{reason}:{route_reason}",
        "model": GROK_MODEL,
    }
