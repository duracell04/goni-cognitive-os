from __future__ import annotations

from datetime import UTC, datetime
import json
import time
from typing import Any

from goni.config import (
    DIFF_THRESHOLD,
    OCR_CHAR_LIMIT,
    POLL_INTERVAL_SECONDS,
    SCREENSHOT_DIR,
)
from goni.memory.sqlite_mem import init_db, log_event, save_perception


def _load_runtime_modules() -> dict[str, Any]:
    import cv2
    import mss
    import numpy as np
    from paddleocr import PaddleOCR
    from PIL import Image
    import uiautomation as auto

    return {
        "auto": auto,
        "cv2": cv2,
        "Image": Image,
        "mss": mss,
        "np": np,
        "PaddleOCR": PaddleOCR,
    }


def capture_screen(sct: Any, monitor: dict, cv2: Any, np: Any) -> Any:
    raw = np.array(sct.grab(monitor))  # BGRA
    return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)


def diff_ratio(prev: Any | None, curr: Any, cv2: Any, np: Any) -> float:
    if prev is None:
        return 1.0

    if prev.shape != curr.shape:
        return 1.0

    diff = cv2.absdiff(prev, curr)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    changed_pixels = np.count_nonzero(gray > 25)
    total_pixels = gray.shape[0] * gray.shape[1]

    return changed_pixels / total_pixels


def save_screenshot(frame: Any, cv2: Any, image_cls: Any) -> str:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    path = SCREENSHOT_DIR / f"screen_{ts}.png"

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_cls.fromarray(rgb).save(path)

    return str(path)


def ocr_frame(frame: Any, ocr: Any) -> str:
    result = ocr.ocr(frame, cls=True)

    if not result or not result[0]:
        return ""

    lines = []
    for item in result[0]:
        try:
            text = item[1][0]
            if text:
                lines.append(text)
        except Exception:
            continue

    return "\n".join(lines)[:OCR_CHAR_LIMIT]


def get_foreground_window_name(auto: Any) -> str:
    try:
        control = auto.GetForegroundControl()
        return control.Name or ""
    except Exception:
        return ""


def get_foreground_ui_elements(auto: Any, limit: int = 40) -> list[dict]:
    elements = []

    try:
        window = auto.GetForegroundControl()
        children = window.GetChildren()
    except Exception:
        return elements

    for control in children[:limit]:
        try:
            rect = control.BoundingRectangle
            if rect.right <= rect.left or rect.bottom <= rect.top:
                continue

            elements.append(
                {
                    "type": control.ControlTypeName or "",
                    "name": control.Name or "",
                    "automation_id": control.AutomationId or "",
                    "bbox": [rect.left, rect.top, rect.right, rect.bottom],
                }
            )
        except Exception:
            continue

    return elements


def build_perception(frame: Any, change: float, runtime: dict[str, Any], ocr: Any) -> dict:
    screenshot_path = save_screenshot(frame, runtime["cv2"], runtime["Image"])

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "change_ratio": round(change, 5),
        "active_window": get_foreground_window_name(runtime["auto"]),
        "ocr_text": ocr_frame(frame, ocr),
        "ui_elements": get_foreground_ui_elements(runtime["auto"]),
        "screenshot_path": screenshot_path,
    }


def main() -> None:
    runtime = _load_runtime_modules()
    ocr = runtime["PaddleOCR"](lang="en", show_log=False)
    sct = runtime["mss"].mss()
    monitor = sct.monitors[1]

    init_db()
    log_event("perception_started", {"monitor": monitor})
    prev_frame = None

    print("GONI perception kernel active. Press Ctrl+C to stop.")

    while True:
        frame = capture_screen(sct, monitor, runtime["cv2"], runtime["np"])
        change = diff_ratio(prev_frame, frame, runtime["cv2"], runtime["np"])

        if change >= DIFF_THRESHOLD:
            perception = build_perception(frame, change, runtime, ocr)
            save_perception(perception)

            preview = {
                "active_window": perception["active_window"],
                "change_ratio": perception["change_ratio"],
                "ocr_preview": perception["ocr_text"][:500],
                "ui_elements_count": len(perception["ui_elements"]),
                "screenshot_path": perception["screenshot_path"],
            }

            print(json.dumps(preview, indent=2, ensure_ascii=False))
            prev_frame = frame

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
