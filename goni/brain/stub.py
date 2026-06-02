from goni.brain.base import BrainResponse
from goni.perception import ScreenContext


class StubBrain:
    async def respond(self, message: str, context: ScreenContext) -> BrainResponse:
        text_count = len(context.visible_text)
        element_count = len(context.ui_elements)
        answer = (
            f"Stub response for '{message}'. "
            f"Active app: {context.active_app}. "
            f"Visible text items: {text_count}. "
            f"UI elements: {element_count}."
        )
        return BrainResponse(answer=answer)
