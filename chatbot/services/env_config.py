"""Read chatbot secrets fresh from .env (Django only loads .env at startup)."""
from pathlib import Path

from dotenv import dotenv_values
from django.conf import settings


def _env_values():
    path = Path(settings.BASE_DIR) / ".env"
    if path.exists():
        return dotenv_values(path)
    return {}


def get_chatbot_provider():
    vals = _env_values()
    return (vals.get("CHATBOT_PROVIDER") or settings.CHATBOT_PROVIDER or "gemini").lower().strip()


def get_gemini_api_key():
    vals = _env_values()
    return (vals.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY or "").strip()


def get_gemini_model():
    vals = _env_values()
    return (vals.get("GEMINI_MODEL") or settings.GEMINI_MODEL or "gemini-flash-latest").strip()


def get_openai_api_key():
    vals = _env_values()
    return (vals.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY or "").strip()


def get_openai_model():
    vals = _env_values()
    return (vals.get("OPENAI_MODEL") or settings.OPENAI_MODEL or "gpt-4o-mini").strip()


def is_chatbot_ready():
    if get_chatbot_provider() == "openai":
        return bool(get_openai_api_key())
    return bool(get_gemini_api_key())
