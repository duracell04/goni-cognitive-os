def build_local_vision_next_step() -> str:
    return "Send screenshot_path + OCR/UI map to local Qwen2.5-VL."


def ask_local_vision_placeholder(
    *,
    user_question: str,
    screenshot_path: str,
    ocr_text: str,
    ui_elements: list[dict],
) -> dict:
    return {
        "provider": "local_qwen_pending",
        "answer": (
            "Local Qwen2.5-VL is not wired yet. "
            "The perception kernel returned the current screen context for inspection."
        ),
        "route_reason": "local_model_placeholder",
        "user_question": user_question,
        "screenshot_path": screenshot_path,
        "ocr_context_preview": ocr_text[:1000],
        "ui_elements": ui_elements[:10],
        "next_step": build_local_vision_next_step(),
    }
