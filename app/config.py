from __future__ import annotations

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

# Current model defaults. These keep the original Flash/Pro role split
# while using currently available Gemini API model names.
GEMINI_OUTLINE_MODEL = os.getenv("GEMINI_OUTLINE_MODEL", "gemini-2.5-flash").strip()
GEMINI_STORY_MODEL = os.getenv("GEMINI_STORY_MODEL", "gemini-2.5-flash").strip()

# Image generation modes:
#   demo     -> local placeholder images so the project runs without any image API
#   hf       -> Hugging Face InferenceClient
#   diffusers -> local Hugging Face Diffusers/Stable Diffusion pipeline
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "demo").strip().lower()
HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL", "stabilityai/stable-diffusion-2-1"
).strip()
LOCAL_DIFFUSION_MODEL = os.getenv(
    "LOCAL_DIFFUSION_MODEL", "stabilityai/stable-diffusion-2-1"
).strip()

DEMO_MODE = os.getenv("DEMO_MODE", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Detect Serverless environments (Vercel, AWS Lambda, Netlify Functions, etc.)
IS_SERVERLESS = bool(
    os.getenv("VERCEL")
    or os.getenv("VERCEL_ENV")
    or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    or os.getenv("LAMBDA_TASK_ROOT")
    or os.getenv("NOW_REGION")
)


def _get_writable_dir(subfolder: str) -> Path:
    """Return a directory guaranteed to be writable on any platform."""
    if IS_SERVERLESS:
        tmp_dir = Path(tempfile.gettempdir()) / "comiccraft" / subfolder
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir

    local_dir = STATIC_DIR / subfolder
    try:
        local_dir.mkdir(parents=True, exist_ok=True)
        test_file = local_dir / f".write_test_{os.getpid()}"
        test_file.touch()
        test_file.unlink(missing_ok=True)
        return local_dir
    except (OSError, PermissionError):
        tmp_dir = Path(tempfile.gettempdir()) / "comiccraft" / subfolder
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir


PANELS_DIR = _get_writable_dir("panels")
EXPORTS_DIR = _get_writable_dir("exports")
