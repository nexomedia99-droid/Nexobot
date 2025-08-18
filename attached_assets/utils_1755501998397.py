import os

# Config from env
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

try:
    OWNER_ID = int(os.getenv("OWNER_ID", "0"))
except ValueError:
    OWNER_ID = 0

def ensure_env():
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if OWNER_ID == 0:
        missing.append("OWNER_ID")
    if missing:
        raise RuntimeError(f"Environment variables missing: {', '.join(missing)}")