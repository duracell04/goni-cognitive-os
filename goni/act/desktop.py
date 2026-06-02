from goni.config import ENABLE_DESKTOP_ACTIONS


ALLOWED_ACTIONS = {
    "mouse.move",
    "mouse.click",
    "keyboard.type",
}


def request_desktop_action(tool_call: dict) -> dict:
    action = tool_call.get("action", "")

    if action not in ALLOWED_ACTIONS:
        return {
            "status": "blocked",
            "reason": "action_not_allowlisted",
            "allowed": sorted(ALLOWED_ACTIONS),
        }

    if not ENABLE_DESKTOP_ACTIONS:
        return {
            "status": "blocked",
            "reason": "desktop_actions_disabled",
            "message": "Set ENABLE_DESKTOP_ACTIONS=true only after adding explicit approval UI.",
        }

    return {
        "status": "pending",
        "message": "Desktop execution wrapper is not implemented yet.",
        "tool_call": tool_call,
    }
