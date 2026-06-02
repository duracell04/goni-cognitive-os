from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
import json
from pathlib import Path


MAX_OCR_CHARS = 3000
MAX_UI_ELEMENTS = 30
MAX_IMAGE_SIDE = 1280
JPEG_QUALITY = 75


@dataclass(frozen=True)
class PreparedVisionPayload:
    user_question: str
    screenshot_path: str
    ocr_text: str
    ui_elements: list[dict]
    active_window: str
    image_mime: str | None
    image_base64: str | None

    @property
    def has_image(self) -> bool:
        return self.image_base64 is not None and self.image_mime is not None

    @property
    def image_data_url(self) -> str | None:
        if not self.has_image:
            return None
        return f"data:{self.image_mime};base64,{self.image_base64}"


def prepare_vision_payload(user_question: str, perception: dict) -> PreparedVisionPayload:
    screenshot_path = perception.get("screenshot_path", "") or ""
    image_mime, image_base64 = _prepare_image(screenshot_path)

    return PreparedVisionPayload(
        user_question=user_question,
        screenshot_path=screenshot_path,
        ocr_text=(perception.get("ocr_text", "") or "")[:MAX_OCR_CHARS],
        ui_elements=(perception.get("ui_elements", []) or [])[:MAX_UI_ELEMENTS],
        active_window=perception.get("active_window", "") or "",
        image_mime=image_mime,
        image_base64=image_base64,
    )


def build_screen_prompt(payload: PreparedVisionPayload) -> str:
    ui_json = json.dumps(payload.ui_elements, ensure_ascii=False, indent=2)
    return f"""
You are GONI, a screen-aware desktop assistant.

Use the screenshot only for the user's current question. Do not assume you are
watching a live stream. The always-on context comes from local OCR and Windows
UI Automation.

Active window:
{payload.active_window}

OCR text:
{payload.ocr_text}

UI elements:
{ui_json}

User question:
{payload.user_question}
""".strip()


def _prepare_image(screenshot_path: str) -> tuple[str | None, str | None]:
    if not screenshot_path:
        return None, None

    path = Path(screenshot_path)
    if not path.exists() or not path.is_file():
        return None, None

    try:
        from PIL import Image

        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
            return "image/jpeg", base64.b64encode(buffer.getvalue()).decode("ascii")
    except Exception:
        return None, None
