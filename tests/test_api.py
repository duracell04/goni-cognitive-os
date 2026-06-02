import sqlite3

from fastapi.testclient import TestClient

from goni.api.main import create_app


def test_health_returns_ok(tmp_path):
    app = create_app(db_path=tmp_path / "goni.sqlite3")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_context_returns_stub_shape(tmp_path):
    app = create_app(db_path=tmp_path / "goni.sqlite3")

    with TestClient(app) as client:
        response = client.get("/context")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_app"] == "GONI Stub Desktop"
    assert payload["visible_text"] == [
        "FastAPI skeleton active",
        "Local perception placeholder",
    ]
    assert payload["screen_changed"] is True
    assert payload["cursor_position"] == {"x": 420, "y": 330}
    assert payload["ui_elements"][0]["bbox"] == [120, 80, 160, 110]


def test_command_returns_stub_answer_and_logs_action(tmp_path):
    db_path = tmp_path / "goni.sqlite3"
    app = create_app(db_path=db_path)

    with TestClient(app) as client:
        response = client.post(
            "/command",
            json={"message": "What am I looking at?", "provider": "stub"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["logged_action_id"] == 1
    assert payload["answer"] == (
        "Stub response for 'What am I looking at?'. "
        "Active app: GONI Stub Desktop. "
        "Visible text items: 2. "
        "UI elements: 2."
    )

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT user_input, provider, result FROM actions WHERE id = 1"
        ).fetchone()

    assert row is not None
    assert row[0] == "What am I looking at?"
    assert row[1] == "stub"
    assert "Stub response" in row[2]
