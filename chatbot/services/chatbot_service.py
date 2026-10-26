"""
AI service layer for the Farmer Chatbot.
Supports Google Gemini and OpenAI, selected via CHATBOT_PROVIDER in .env.
Never hardcodes API keys - always reads from environment via settings.
Fails gracefully (returns a friendly message) if no key is configured or
if the provider API call fails for any reason.
"""
import logging

import requests

from .env_config import (
    get_chatbot_provider,
    get_gemini_api_key,
    get_gemini_model,
    get_openai_api_key,
    get_openai_model,
)

logger = logging.getLogger("sprigai")

SYSTEM_INSTRUCTION = (
    "You are SprigAI's Farmer Assistant, a helpful agriculture chatbot for farmers in "
    "Bangladesh. Answer questions about crops, fertilizer, soil, plant disease, "
    "irrigation, seasons, weather, harvest timing, and general smart agriculture in "
    "simple, clear language. Give practical, actionable advice tailored to Bangladesh's "
    "climate and farming conditions. You support - but never replace - official "
    "agricultural expert advice. If a question involves pesticides, chemicals, medical "
    "treatment, or other safety-sensitive topics, give cautious, general guidance and "
    "recommend the user verify with their local agricultural office or a qualified "
    "expert before acting. Keep answers concise, friendly, and practical."
)

SAFETY_SENSITIVE_KEYWORDS = [
    "pesticide", "insecticide", "fungicide", "herbicide", "poison", "chemical dose",
    "toxic", "overdose", "medicine", "medical",
]

SAFETY_NOTE = (
    "\n\n⚠️ This involves chemicals/safety-sensitive information. Please verify "
    "exact products and dosages with your local agricultural extension office or "
    "a licensed expert before use."
)


class ChatbotUnavailableError(Exception):
    pass


def _is_safety_sensitive(text: str) -> bool:
    lowered = text.lower()
    return any(k in lowered for k in SAFETY_SENSITIVE_KEYWORDS)


def _extract_gemini_text(data: dict) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError("Gemini returned no candidates.")
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text_parts = [p.get("text", "") for p in parts if p.get("text")]
    if not text_parts:
        raise ValueError("Gemini returned an empty response.")
    return "".join(text_parts).strip()


def _call_gemini(message, history):
    api_key = get_gemini_api_key()
    model = get_gemini_model()
    if not api_key:
        raise ChatbotUnavailableError("Gemini API key is not configured.")

    contents = []
    for m in history:
        role = "user" if m["sender"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    contents.append({"role": "user", "parts": [{"text": message}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        },
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=45)
    if not resp.ok:
        logger.error("Gemini API error %s: %s", resp.status_code, resp.text[:500])
    resp.raise_for_status()
    return _extract_gemini_text(resp.json())


def _call_openai(message, history):
    api_key = get_openai_api_key()
    model = get_openai_model()
    if not api_key:
        raise ChatbotUnavailableError("OpenAI API key is not configured.")

    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for m in history:
        role = "user" if m["sender"] == "user" else "assistant"
        messages.append({"role": role, "content": m["content"]})
    messages.append({"role": "user", "content": message})

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": 0.6}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def get_bot_reply(message, history=None):
    """
    history: list of {"sender": "user"|"bot", "content": str}
    Returns dict: {success, error, reply}
    """
    history = history or []
    provider = get_chatbot_provider()

    try:
        if provider == "openai":
            reply = _call_openai(message, history)
        else:
            reply = _call_gemini(message, history)

        if _is_safety_sensitive(message):
            reply = reply.rstrip() + SAFETY_NOTE

        return {"success": True, "error": None, "reply": reply}
    except ChatbotUnavailableError as exc:
        logger.warning("Chatbot unavailable: %s", exc)
        return {
            "success": False,
            "error": str(exc),
            "reply": (
                "The AI chatbot isn't configured yet (missing API key), but the rest "
                "of SprigAI is fully available. Please try the other AI modules, or "
                "ask an administrator to add a chatbot API key in the .env file."
            ),
        }
    except requests.HTTPError as exc:
        logger.exception("Chatbot API HTTP error")
        status = exc.response.status_code if exc.response is not None else None
        if status == 429:
            reply = "I'm receiving too many requests right now. Please wait a moment and try again."
        elif status in (401, 403):
            reply = "The AI service rejected our API key. Please ask an administrator to check the Gemini API key in .env."
        elif status == 404:
            reply = "The configured AI model is unavailable. Please update GEMINI_MODEL in .env and restart the server."
        else:
            reply = "Sorry, I couldn't reach the AI service right now. Please try again in a moment."
        return {"success": False, "error": "chatbot_api_error", "reply": reply}
    except requests.RequestException:
        logger.exception("Chatbot API request failed")
        return {
            "success": False,
            "error": "chatbot_api_error",
            "reply": "Sorry, I couldn't reach the AI service right now. Please try again in a moment.",
        }
    except Exception:
        logger.exception("Unexpected chatbot error")
        return {
            "success": False,
            "error": "unexpected_error",
            "reply": "Something went wrong while generating a response. Please try again.",
        }
