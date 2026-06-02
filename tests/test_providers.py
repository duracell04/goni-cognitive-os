from pathlib import Path

from goni.decide import brain_gemini, brain_grok
from goni.decide.vision_payload import build_screen_prompt, prepare_vision_payload


def test_prepare_vision_payload_uses_local_context_without_streaming():
    payload = prepare_vision_payload(
        "Explain this error",
        {
            "active_window": "Terminal",
            "ocr_text": "ValueError: invalid literal",
            "ui_elements": [{"type": "TextControl", "name": "Traceback"}],
            "screenshot_path": "missing.png",
        },
    )

    prompt = build_screen_prompt(payload)

    assert payload.image_base64 is None
    assert payload.image_mime is None
    assert "ValueError: invalid literal" in prompt
    assert "Traceback" in prompt
    assert "Do not assume you are\nwatching a live stream" in prompt


def test_gemini_provider_builds_payload_with_mocked_http(monkeypatch):
    captured = {}

    def fake_post_json(url, body):
        captured["url"] = url
        captured["body"] = body
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "The screen shows a terminal error."}]
                    }
                }
            ]
        }

    monkeypatch.setattr(brain_gemini, "GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(brain_gemini, "_post_json", fake_post_json)
    payload = prepare_vision_payload(
        "Explain",
        {
            "active_window": "Terminal",
            "ocr_text": "error",
            "ui_elements": [],
            "screenshot_path": "",
        },
    )

    result = brain_gemini.ask_gemini_vision(payload)

    assert result["provider"] == "gemini"
    assert result["answer"] == "The screen shows a terminal error."
    assert "generateContent" in captured["url"]
    assert captured["body"]["contents"][0]["parts"][0]["text"].startswith("You are GONI")


def test_grok_provider_builds_payload_with_mocked_http(monkeypatch):
    captured = {}

    def fake_post_json(url, body):
        captured["url"] = url
        captured["body"] = body
        return {"output_text": "Next, inspect the failing command."}

    monkeypatch.setattr(brain_grok, "XAI_API_KEY", "test-key")
    monkeypatch.setattr(brain_grok, "_post_json", fake_post_json)
    payload = prepare_vision_payload(
        "What next?",
        {
            "active_window": "Terminal",
            "ocr_text": "pytest failed",
            "ui_elements": [],
            "screenshot_path": "",
        },
    )

    result = brain_grok.ask_grok_vision(payload, route_reason="explicit_grok")

    assert result["provider"] == "grok"
    assert result["answer"] == "Next, inspect the failing command."
    assert captured["url"].endswith("/responses")
    assert captured["body"]["store"] is False
    assert captured["body"]["input"][0]["content"][0]["type"] == "input_text"
