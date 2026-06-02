from datetime import UTC, datetime
from pathlib import Path

import aiosqlite

from goni.brain.base import BrainResponse
from goni.perception import ScreenContext


class ActionLogStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    async def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="utf-8")
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript(schema)
            await db.commit()

    async def log_action(
        self,
        *,
        user_input: str,
        screen_context: ScreenContext,
        provider: str,
        result: BrainResponse,
    ) -> int:
        timestamp = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO actions (ts, user_input, screen_context, provider, result)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    timestamp,
                    user_input,
                    screen_context.model_dump_json(),
                    provider,
                    result.model_dump_json(),
                ),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def count_actions(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM actions")
            row = await cursor.fetchone()
            return int(row[0])
