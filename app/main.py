from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import STATIC_DIR
from .routes import router

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate a personalized five-panel comic with Gemini and Hugging Face image generation.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)
