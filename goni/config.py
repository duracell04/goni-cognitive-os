from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> None:
        return None


load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
DB_PATH = DATA_DIR / "goni.db"

DATA_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)

DIFF_THRESHOLD = float(os.getenv("DIFF_THRESHOLD", "0.02"))
POLL_INTERVAL_SECONDS = float(os.getenv("POLL_INTERVAL_SECONDS", "0.5"))
OCR_CHAR_LIMIT = int(os.getenv("OCR_CHAR_LIMIT", "3000"))

LOCAL_LLM_BASE_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen2.5-vl-7b-instruct")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ENABLE_DESKTOP_ACTIONS = os.getenv("ENABLE_DESKTOP_ACTIONS", "false").lower() == "true"
