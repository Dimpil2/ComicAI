from __future__ import annotations

from functools import lru_cache

from .config import GEMINI_API_KEY

try:
    from google import genai
except ImportError:  # pragma: no cover
    genai = None


@lru_cache(maxsize=1)
def get_client():
    if genai is None:
        raise RuntimeError(
            "The google-genai package is not installed. Run: python -m pip install -r requirements.txt"
        )
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to ComicCraft/.env before generating an AI comic."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt: str, model: str, json_mode: bool = False) -> str:
    client = get_client()
    kwargs = {"response_mime_type": "application/json"} if json_mode else {}
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=kwargs or None,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
