from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3

from goni.config import DB_PATH


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class SQLiteMemory:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self.db_path = Path(db_path)

    def init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS perceptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    active_window TEXT,
                    change_ratio REAL,
                    ocr_text TEXT,
                    ui_elements_json TEXT,
                    screenshot_path TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body TEXT,
                    source TEXT,
                    tags_json TEXT
                )
                """
            )
            conn.commit()

    def log_event(self, event_type: str, payload: dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO session_logs (ts, event_type, payload_json) VALUES (?, ?, ?)",
                (utc_now(), event_type, json.dumps(payload, ensure_ascii=False)),
            )
            conn.commit()

    def save_perception(self, perception: dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO perceptions (
                    ts,
                    active_window,
                    change_ratio,
                    ocr_text,
                    ui_elements_json,
                    screenshot_path
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    perception.get("active_window", ""),
                    perception.get("change_ratio", 0.0),
                    perception.get("ocr_text", ""),
                    json.dumps(perception.get("ui_elements", []), ensure_ascii=False),
                    perception.get("screenshot_path", ""),
                ),
            )
            conn.commit()

    def latest_perception(self) -> dict | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM perceptions ORDER BY id DESC LIMIT 1"
            ).fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "ts": row["ts"],
            "active_window": row["active_window"],
            "change_ratio": row["change_ratio"],
            "ocr_text": row["ocr_text"],
            "ui_elements": json.loads(row["ui_elements_json"] or "[]"),
            "screenshot_path": row["screenshot_path"],
        }

    def save_knowledge_node(
        self,
        *,
        title: str,
        body: str,
        source: str = "",
        tags: list[str] | None = None,
    ) -> int:
        tags = tags or []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO knowledge_nodes (ts, title, body, source, tags_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (utc_now(), title, body, source, json.dumps(tags, ensure_ascii=False)),
            )
            conn.commit()
            return int(cursor.lastrowid)


_default_memory = SQLiteMemory()


def init_db() -> None:
    _default_memory.init_db()


def log_event(event_type: str, payload: dict) -> None:
    _default_memory.log_event(event_type, payload)


def save_perception(perception: dict) -> None:
    _default_memory.save_perception(perception)


def latest_perception() -> dict | None:
    return _default_memory.latest_perception()


def save_knowledge_node(
    title: str, body: str, source: str = "", tags: list[str] | None = None
) -> int:
    return _default_memory.save_knowledge_node(
        title=title,
        body=body,
        source=source,
        tags=tags,
    )
