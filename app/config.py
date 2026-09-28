from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

# Current model defaults. These keep the original Flash/Pro role split
# while using currently available Gemini API model names.
GEMINI_OUTLINE_MODEL = os.getenv("GEMINI_OUTLINE_MODEL", "gemini-3.8-flash").strip()
GEMINI_STORY_MODEL = os.getenv("GEMINI_STORY_MODEL", "gemini-3.8-flash").strip()

# Image generation modes:
#   demo     -> local placeholder images so the project runs without any image API
#   hf       -> Hugging Face InferenceClient
#   diffusers -> local Hugging Face Diffusers/Stable Diffusion pipeline
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "demo").strip().lower()
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL", "stable-diffusion-v1-5/stable-diffusion-v1-5"
).strip()
LOCAL_DIFFUSION_MODEL = os.getenv(
    "LOCAL_DIFFUSION_MODEL", "stable-diffusion-v1-5/stable-diffusion-v1-5"
).strip()

DEMO_MODE = os.getenv("DEMO_MODE", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
TEMPLATES_DIR = BASE_DIR / "templates"

for directory in (PANELS_DIR, EXPORTS_DIR, TEMPLATES_DIR):
    directory.mkdir(parents=True, exist_ok=True)
