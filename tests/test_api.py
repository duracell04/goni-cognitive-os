import sqlite3

from fastapi.testclient import TestClient

from goni.api.main import create_app as create_compat_app
from goni.decide.server import create_app
from goni.memory.sqlite_mem import SQLiteMemory


def seed_perception(db_path):
    memory = SQLiteMemory(db_path)
    memory.init_db()
    memory.save_perception(
        {
            "active_window": "VS Code",
            "change_ratio": 0.42,
            "ocr_text": "Traceback\nValueError: invalid literal",
            "ui_elements": [
                {
                    "type": "ButtonControl",
                    "name": "Run",
                    "automation_id": "run-button",
                    "bbox": [120, 80, 160, 110],
                }
            ],
            "screenshot_path": "data/screenshots/screen_test.png",
        }
    )


def test_health_returns_ok(tmp_path):
    app = create_app(db_path=tmp_path / "goni.db")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_main_reexports_canonical_app_factory(tmp_path):
    app = create_compat_app(db_path=tmp_path / "goni.db")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_context_returns_empty_state_before_perception(tmp_path):
    app = create_app(db_path=tmp_path / "goni.db")

    with TestClient(app) as client:
        response = client.get("/context")

    assert response.status_code == 200
    assert response.json() == {
        "status": "empty",
        "message": "No perception captured yet. Run python -m goni.perceive.perceive first.",
    }


def test_context_returns_latest_seeded_perception(tmp_path):
    db_path = tmp_path / "goni.db"
    seed_perception(db_path)
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        response = client.get("/context")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["context"]["active_window"] == "VS Code"
    assert payload["context"]["change_ratio"] == 0.42
    assert payload["context"]["ocr_text"] == "Traceback\nValueError: invalid literal"
    assert payload["context"]["ui_elements"][0]["bbox"] == [120, 80, 160, 110]


def test_command_returns_gemini_unavailable_without_key(tmp_path):
    db_path = tmp_path / "goni.db"
    seed_perception(db_path)
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        response = client.post(
            "/command",
            json={"text": "What am I looking at?"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["provider"] == "gemini_unavailable"
    assert payload["route_reason"] == "provider_unavailable:missing_api_key"
    assert payload["active_window"] == "VS Code"
    assert payload["ocr_context_preview"] == "Traceback\nValueError: invalid literal"
    assert payload["ui_elements"][0]["name"] == "Run"
    assert payload["screenshot_path"] == "data/screenshots/screen_test.png"

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT event_type FROM session_logs ORDER BY id"
        ).fetchall()

    assert ("user_command",) in rows
    assert ("assistant_answer",) in rows


def test_command_accepts_explicit_grok_provider(tmp_path):
    db_path = tmp_path / "goni.db"
    seed_perception(db_path)
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        response = client.post(
            "/command",
            json={"text": "What should I do next?", "provider": "grok"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "grok_unavailable"
    assert payload["route_reason"] == "provider_unavailable:missing_api_key:explicit_grok"


def test_command_accepts_explicit_local_provider(tmp_path):
    db_path = tmp_path / "goni.db"
    seed_perception(db_path)
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        response = client.post(
            "/command",
            json={"text": "Explain privately", "provider": "local"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["provider"] == "local_qwen_disabled"
    assert payload["route_reason"] == "local_model_disabled"


def test_desktop_action_is_disabled_by_default(tmp_path):
    app = create_app(db_path=tmp_path / "goni.db")

    with TestClient(app) as client:
        response = client.post("/act/desktop", json={"action": "mouse.click"})

    assert response.status_code == 200
    assert response.json()["reason"] == "desktop_actions_disabled"
