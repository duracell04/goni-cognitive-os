from goni.config import LOCAL_LLM_ENABLED, LOCAL_LLM_MODEL
from goni.decide.vision_payload import PreparedVisionPayload


def ask_local_vision_placeholder(payload: PreparedVisionPayload) -> dict:
    if not LOCAL_LLM_ENABLED:
        return {
            "provider": "local_qwen_disabled",
            "answer": (
                "Local Qwen is disabled for V1. Use Gemini for default screen explanation, "
                "or enable local offline mode later with LOCAL_LLM_ENABLED=true."
            ),
            "route_reason": "local_model_disabled",
            "user_question": payload.user_question,
            "screenshot_path": payload.screenshot_path,
            "ocr_context_preview": payload.ocr_text[:1000],
            "ui_elements": payload.ui_elements[:10],
            "next_step": "Use Gemini Flash-Lite by default; reserve Qwen for offline/private mode.",
        }

    return {
        "provider": "local_qwen_pending",
        "answer": (
            "Local Qwen is enabled in configuration, but the LM Studio/Ollama call is not wired yet."
        ),
        "route_reason": "local_model_pending",
        "user_question": payload.user_question,
        "screenshot_path": payload.screenshot_path,
        "ocr_context_preview": payload.ocr_text[:1000],
        "ui_elements": payload.ui_elements[:10],
        "next_step": f"Wire {LOCAL_LLM_MODEL or 'a local Qwen2.5-VL model'} through LM Studio or Ollama.",
    }
