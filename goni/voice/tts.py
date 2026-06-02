def speak_placeholder(text: str) -> dict:
    return {
        "status": "disabled",
        "message": "Local text-to-speech is not implemented in V1.",
        "text": text,
    }
