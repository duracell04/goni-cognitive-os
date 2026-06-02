from goni.decide.brain_local import ask_local_vision_placeholder


def answer_screen_question(user_question: str, perception: dict) -> dict:
    return ask_local_vision_placeholder(
        user_question=user_question,
        screenshot_path=perception.get("screenshot_path", ""),
        ocr_text=perception.get("ocr_text", ""),
        ui_elements=perception.get("ui_elements", []),
    )
