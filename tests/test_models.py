from goni.perception import CursorPosition, ScreenContext, UiElement


def test_screen_context_serializes_as_structured_json():
    context = ScreenContext(
        active_app="VS Code",
        visible_text=["main.py", "Traceback"],
        ui_elements=[
            UiElement(type="tab", label="main.py", bbox=(20, 40, 95, 68)),
        ],
        cursor_position=CursorPosition(x=10, y=20),
        screen_changed=True,
    )

    payload = context.model_dump(mode="json")

    assert payload["active_app"] == "VS Code"
    assert payload["visible_text"] == ["main.py", "Traceback"]
    assert payload["ui_elements"][0]["bbox"] == [20, 40, 95, 68]
    assert payload["cursor_position"] == {"x": 10, "y": 20}
    assert payload["screen_changed"] is True
