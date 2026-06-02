from typing import Protocol

from pydantic import BaseModel

from goni.perception import ScreenContext


class BrainResponse(BaseModel):
    answer: str


class BrainProvider(Protocol):
    async def respond(self, message: str, context: ScreenContext) -> BrainResponse:
        """Return a response for a user command and structured screen context."""
