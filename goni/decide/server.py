from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from goni import __version__
from goni.act.desktop import request_desktop_action
from goni.config import DB_PATH
from goni.decide.router import answer_screen_question
from goni.memory.sqlite_mem import SQLiteMemory


class HealthResponse(BaseModel):
    status: str
    version: str


class CommandRequest(BaseModel):
    text: str = Field(min_length=1)


class SaveKnowledgeRequest(BaseModel):
    title: str = Field(min_length=1)
    body: str = ""
    source: str = ""
    tags: list[str] = Field(default_factory=list)


def create_app(*, db_path: str | Path = DB_PATH) -> FastAPI:
    memory = SQLiteMemory(db_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        memory.init_db()
        memory.log_event("server_started", {})
        app.state.memory = memory
        yield

    app = FastAPI(
        title="GONI Cognitive OS",
        version=__version__,
        lifespan=lifespan,
    )

    @app.get("/")
    def root() -> dict:
        return {
            "name": "GONI Cognitive OS",
            "status": "running",
            "endpoints": ["/health", "/context", "/command", "/knowledge"],
        }

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", version=__version__)

    @app.get("/context")
    def get_context(request: Request) -> dict:
        store: SQLiteMemory = request.app.state.memory
        perception = store.latest_perception()

        if perception is None:
            return {
                "status": "empty",
                "message": "No perception captured yet. Run python -m goni.perceive.perceive first.",
            }

        return {
            "status": "ok",
            "context": perception,
        }

    @app.post("/command")
    def command(req: CommandRequest, request: Request) -> dict:
        store: SQLiteMemory = request.app.state.memory
        perception = store.latest_perception()

        if perception is None:
            return {
                "status": "empty",
                "message": "No perception available yet.",
            }

        store.log_event("user_command", {"text": req.text})
        result = answer_screen_question(req.text, perception)
        store.log_event(
            "assistant_answer",
            {
                "question": req.text,
                "provider": result["provider"],
                "route_reason": result["route_reason"],
                "answer": result["answer"],
            },
        )

        return {
            "status": "ok",
            "active_window": perception["active_window"],
            **result,
        }

    @app.post("/knowledge")
    def knowledge(req: SaveKnowledgeRequest, request: Request) -> dict:
        store: SQLiteMemory = request.app.state.memory
        node_id = store.save_knowledge_node(
            title=req.title,
            body=req.body,
            source=req.source,
            tags=req.tags,
        )
        return {"status": "ok", "node_id": node_id}

    @app.post("/act/desktop")
    def act_desktop(tool_call: dict) -> dict:
        return request_desktop_action(tool_call)

    return app


app = create_app()
