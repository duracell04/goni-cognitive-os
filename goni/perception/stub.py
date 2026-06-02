from goni.perception.models import CursorPosition, ScreenContext, UiElement


class StubPerceptionService:
    async def get_latest_context(self) -> ScreenContext:
        return ScreenContext(
            active_app="GONI Stub Desktop",
            visible_text=[
                "FastAPI skeleton active",
                "Local perception placeholder",
            ],
            ui_elements=[
                UiElement(type="button", label="Run", bbox=(120, 80, 160, 110)),
                UiElement(type="panel", label="Context", bbox=(20, 40, 420, 320)),
            ],
            cursor_position=CursorPosition(x=420, y=330),
            screen_changed=True,
        )
