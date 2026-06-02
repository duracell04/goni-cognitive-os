from goni.memory.sqlite_mem import SQLiteMemory


def test_sqlite_memory_saves_and_loads_latest_perception(tmp_path):
    db_path = tmp_path / "goni.db"
    memory = SQLiteMemory(db_path)
    memory.init_db()

    memory.save_perception(
        {
            "active_window": "Terminal",
            "change_ratio": 0.15,
            "ocr_text": "pytest passed",
            "ui_elements": [
                {
                    "type": "TextControl",
                    "name": "pytest passed",
                    "automation_id": "",
                    "bbox": [10, 20, 300, 40],
                }
            ],
            "screenshot_path": "data/screenshots/screen_terminal.png",
        }
    )

    perception = memory.latest_perception()

    assert perception is not None
    assert perception["active_window"] == "Terminal"
    assert perception["change_ratio"] == 0.15
    assert perception["ocr_text"] == "pytest passed"
    assert perception["ui_elements"] == [
        {
            "type": "TextControl",
            "name": "pytest passed",
            "automation_id": "",
            "bbox": [10, 20, 300, 40],
        }
    ]
    assert perception["screenshot_path"] == "data/screenshots/screen_terminal.png"
