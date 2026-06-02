from datetime import UTC, datetime

from pydantic import BaseModel, Field


class CursorPosition(BaseModel):
    x: int
    y: int


class UiElement(BaseModel):
    type: str
    label: str
    bbox: tuple[int, int, int, int] = Field(
        description="Screen-space bounding box as x1, y1, x2, y2."
    )


class ScreenContext(BaseModel):
    active_app: str
    visible_text: list[str]
    ui_elements: list[UiElement]
    cursor_position: CursorPosition
    screen_changed: bool
    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
