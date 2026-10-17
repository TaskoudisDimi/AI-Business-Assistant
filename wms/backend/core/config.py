import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Public URL of the frontend — used for email links (confirmation, password reset)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# Outgoing email (alerts, team notices). Use the same SMTP provider as Supabase Auth.
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "WMS <no-reply@task-code.com>")

# AI features (invoice scanning, assistant, message drafts). Off when no key is set.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "claude-opus-5-5")
AI_DAILY_LIMIT = int(os.getenv("AI_DAILY_LIMIT", "200"))   # requests per business per day
