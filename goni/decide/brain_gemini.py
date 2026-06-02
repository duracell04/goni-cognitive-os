from __future__ import annotations

import json
from urllib import error, request

from goni.config import GEMINI_API_KEY, GEMINI_MODEL
from goni.decide.vision_payload import PreparedVisionPayload, build_screen_prompt


def ask_gemini_vision(payload: PreparedVisionPayload) -> dict:
    if not GEMINI_API_KEY:
        return _unavailable(payload, "missing_api_key")

    parts = [{"text": build_screen_prompt(payload)}]
    if payload.has_image:
        parts.append(
            {
                "inline_data": {
                    "mime_type": payload.image_mime,
                    "data": payload.image_base64,
                }
            }
        )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": parts,
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )

    try:
        data = _post_json(url, body)
        answer = _extract_answer(data)
    except Exception as exc:
        return {
            **_base_response(payload),
            "provider": "gemini_unavailable",
            "answer": "Gemini request failed. Grok fallback may handle this if configured.",
            "route_reason": "provider_error",
            "error": str(exc),
            "fallback_recommended": True,
        }

    return {
        **_base_response(payload),
        "provider": "gemini",
        "answer": answer,
        "route_reason": "default_gemini",
        "model": GEMINI_MODEL,
        "fallback_recommended": _is_weak_answer(answer),
    }


def _post_json(url: str, body: dict) -> dict:
    encoded = json.dumps(body).encode("utf-8")
    req = request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def _extract_answer(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    return "\n".join(part.get("text", "") for part in parts).strip()


def _is_weak_answer(answer: str) -> bool:
    stripped = answer.strip()
    return len(stripped) < 40


def _base_response(payload: PreparedVisionPayload) -> dict:
    return {
        "user_question": payload.user_question,
        "screenshot_path": payload.screenshot_path,
        "ocr_context_preview": payload.ocr_text[:1000],
        "ui_elements": payload.ui_elements[:10],
    }


def _unavailable(payload: PreparedVisionPayload, reason: str) -> dict:
    return {
        **_base_response(payload),
        "provider": "gemini_unavailable",
        "answer": "Gemini is not configured. Set GEMINI_API_KEY to enable the default vision brain.",
        "route_reason": f"provider_unavailable:{reason}",
        "model": GEMINI_MODEL,
        "fallback_recommended": True,
    }
