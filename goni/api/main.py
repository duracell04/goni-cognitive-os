from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from goni import __version__
from goni.brain import BrainProvider, StubBrain
from goni.memory import ActionLogStore
from goni.perception import ScreenContext, StubPerceptionService


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class CommandRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: Literal["stub"] = "stub"


class CommandResponse(BaseModel):
    answer: str
    context: ScreenContext
    logged_action_id: int


def create_app(
    *,
    db_path: str | Path = "data/goni.sqlite3",
    perception_service: StubPerceptionService | None = None,
    brain_providers: dict[str, BrainProvider] | None = None,
) -> FastAPI:
    memory = ActionLogStore(db_path)
    perception = perception_service or StubPerceptionService()
    providers: dict[str, BrainProvider] = brain_providers or {"stub": StubBrain()}

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        await memory.initialize()
        app.state.memory = memory
        app.state.perception = perception
        app.state.brain_providers = providers
        yield

    app = FastAPI(
        title="GONI Cognitive OS API",
        version=__version__,
        lifespan=lifespan,
    )

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__)

    @app.get("/context", response_model=ScreenContext)
    async def context(request: Request) -> ScreenContext:
        service: StubPerceptionService = request.app.state.perception
        return await service.get_latest_context()

    @app.post("/command", response_model=CommandResponse)
    async def command(payload: CommandRequest, request: Request) -> CommandResponse:
        providers: dict[str, BrainProvider] = request.app.state.brain_providers
        provider = providers.get(payload.provider)
        if provider is None:
            raise HTTPException(status_code=400, detail="Unsupported brain provider")

        service: StubPerceptionService = request.app.state.perception
        memory_store: ActionLogStore = request.app.state.memory
        screen_context = await service.get_latest_context()
        brain_response = await provider.respond(payload.message, screen_context)
        action_id = await memory_store.log_action(
            user_input=payload.message,
            screen_context=screen_context,
            provider=payload.provider,
            result=brain_response,
        )

        return CommandResponse(
            answer=brain_response.answer,
            context=screen_context,
            logged_action_id=action_id,
        )

    return app


app = create_app()
