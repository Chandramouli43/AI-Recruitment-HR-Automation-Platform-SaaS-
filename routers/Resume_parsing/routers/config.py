import os
from dotenv import load_dotenv

# Load environment variables from .env at project root
load_dotenv()

def require_env(key: str) -> str:
    """Raise an error if required env var is missing."""
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val

OPENAI_API_KEY = require_env("OPENAI_API_KEY")
DATABASE_URL   = require_env("DATABASE_URL")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = require_env("SMTP_USER")
SMTP_PASS = require_env("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

SCORE_THRESHOLD = float(require_env("SCORE_THRESHOLD"))

# Debug print to confirm values loaded
print(f"[CONFIG] SCORE_THRESHOLD loaded: {SCORE_THRESHOLD}")
