from goni.decide.router import answer_screen_question


def perception():
    return {
        "active_window": "Browser",
        "ocr_text": "Search results for FastAPI",
        "ui_elements": [{"type": "EditControl", "name": "Search", "bbox": [1, 2, 3, 4]}],
        "screenshot_path": "",
    }


def test_auto_selects_gemini_by_default_with_mock_client():
    calls = []

    def fake_gemini(payload):
        calls.append(payload)
        return {
            "provider": "gemini",
            "answer": "This is a browser search results page.",
            "route_reason": "default_gemini",
            "fallback_recommended": False,
            "screenshot_path": payload.screenshot_path,
            "ocr_context_preview": payload.ocr_text,
            "ui_elements": payload.ui_elements,
        }

    result = answer_screen_question(
        "What am I looking at?",
        perception(),
        gemini_client=fake_gemini,
    )

    assert result["provider"] == "gemini"
    assert len(calls) == 1


def test_explicit_grok_selects_grok_with_mock_client():
    calls = []

    def fake_grok(payload, *, route_reason):
        calls.append((payload, route_reason))
        return {
            "provider": "grok",
            "answer": "Use the search box to refine the query.",
            "route_reason": route_reason,
            "screenshot_path": payload.screenshot_path,
            "ocr_context_preview": payload.ocr_text,
            "ui_elements": payload.ui_elements,
        }

    result = answer_screen_question(
        "What should I do next?",
        perception(),
        provider="grok",
        grok_client=fake_grok,
    )

    assert result["provider"] == "grok"
    assert result["route_reason"] == "explicit_grok"
    assert len(calls) == 1


def test_local_provider_returns_disabled_placeholder():
    result = answer_screen_question("Explain privately", perception(), provider="local")

    assert result["provider"] == "local_qwen_disabled"
    assert result["route_reason"] == "local_model_disabled"


def test_gemini_weak_result_falls_back_to_grok():
    def weak_gemini(payload):
        return {
            "provider": "gemini",
            "answer": "",
            "route_reason": "default_gemini",
            "fallback_recommended": True,
        }

    def fake_grok(payload, *, route_reason):
        return {
            "provider": "grok",
            "answer": "Fallback answer.",
            "route_reason": route_reason,
        }

    result = answer_screen_question(
        "Explain this",
        perception(),
        gemini_client=weak_gemini,
        grok_client=fake_grok,
    )

    assert result["provider"] == "grok"
    assert result["route_reason"] == "gemini_fallback"


def test_missing_gemini_key_does_not_fallback_to_missing_grok():
    result = answer_screen_question("Explain this", perception())

    assert result["provider"] == "gemini_unavailable"
    assert result["route_reason"] == "provider_unavailable:missing_api_key"
