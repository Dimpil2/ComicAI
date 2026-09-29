from __future__ import annotations

import base64
import random
import re
import urllib.parse
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from .config import (
    DEMO_MODE,
    HF_IMAGE_MODEL,
    HF_TOKEN,
    IMAGE_PROVIDER,
    LOCAL_DIFFUSION_MODEL,
    PANELS_DIR,
)

_PIPELINE = None


class GeneratedImage(dict):
    """Dict containing image metadata and Base64 data URL, with str compatibility."""
    def __init__(self, path: str, data_url: str, filename: str):
        super().__init__(path=path, data_url=data_url, filename=filename)
        self.path = path
        self.data_url = data_url
        self.filename = filename

    def __str__(self) -> str:
        return self.path


def sanitize_filename(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", text.strip().lower()).strip("_")
    return value[:80] or "panel"


def _load_font(size: int):
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeui.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _get_theme_palette(prompt: str) -> tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]:
    p = prompt.lower()
    if any(w in p for w in ["forest", "tree", "woods", "nature", "jungle", "fox"]):
        return ((20, 50, 35), (42, 110, 75), (240, 180, 70))
    elif any(w in p for w in ["space", "star", "alien", "galaxy", "nebula", "planet"]):
        return ((15, 18, 45), (45, 30, 90), (100, 220, 255))
    elif any(w in p for w in ["city", "cyber", "neon", "skyscraper", "street"]):
        return ((25, 20, 48), (85, 35, 95), (255, 105, 180))
    elif any(w in p for w in ["school", "classroom", "student", "teacher", "science"]):
        return ((30, 55, 80), (60, 115, 160), (255, 210, 80))
    else:
        return ((35, 45, 60), (70, 95, 130), (255, 170, 60))


def _demo_image(prompt: str, filename: str) -> GeneratedImage:
    width, height = 768, 512
    top_color, mid_color, accent_color = _get_theme_palette(prompt)
    
    image = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + mid_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + mid_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + mid_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    for _ in range(35):
        cx = random.randint(30, width - 30)
        cy = random.randint(30, height - 120)
        cr = random.randint(2, 6)
        draw.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(accent_color[0], accent_color[1], accent_color[2], 120))

    draw.rectangle((16, 16, width - 16, height - 16), outline=(255, 255, 255), width=3)
    draw.rectangle((20, 20, width - 20, height - 20), outline=(15, 23, 42), width=2)

    title_font = _load_font(24)
    body_font = _load_font(15)
    badge_font = _load_font(13)

    draw.rounded_rectangle((36, 32, 220, 68), radius=8, fill=(15, 23, 42))
    draw.text((48, 42), "COMICCRAFT AI", font=badge_font, fill=accent_color)
    draw.text((40, 90), "Illustrated Scene", font=title_font, fill=(255, 255, 255))

    clean_text = prompt.replace("\n", " ").strip()
    if len(clean_text) > 280:
        clean_text = clean_text[:277] + "..."

    draw.rounded_rectangle((36, height - 170, width - 36, height - 36), radius=12, fill=(10, 15, 28))
    draw.rectangle((36, height - 170, width - 36, height - 36), outline=(60, 80, 110), width=1)
    
    words = clean_text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        if len(" ".join(current_line)) > 72:
            lines.append(" ".join(current_line[:-1]))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    y_text = height - 154
    for line in lines[:4]:
        draw.text((54, y_text), line, font=body_font, fill=(230, 240, 255))
        y_text += 24

    path = PANELS_DIR / filename
    try:
        image.save(path, format="PNG")
    except Exception:
        pass

    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"
    return GeneratedImage(path=str(path), data_url=data_url, filename=filename)


def _cloud_ai_image(prompt: str) -> Image.Image:
    """Generate real AI comic artwork from cloud image pipeline."""
    clean_prompt = prompt.replace("\n", " ").strip()
    encoded = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=512&nologo=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=12)
    if response.status_code == 200 and len(response.content) > 1000:
        return Image.open(BytesIO(response.content)).convert("RGB")
    raise RuntimeError(f"Cloud image service returned status {response.status_code}")


def _hf_image(prompt: str) -> Image.Image:
    from huggingface_hub import InferenceClient

    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is missing.")
    client = InferenceClient(api_key=HF_TOKEN, provider="auto")
    return client.text_to_image(prompt=prompt, model=HF_IMAGE_MODEL)


def _diffusers_image(prompt: str) -> Image.Image:
    global _PIPELINE
    try:
        import torch
        from diffusers import AutoPipelineForText2Image
    except ImportError as exc:
        raise RuntimeError(
            "Diffusers mode needs torch, diffusers, transformers, and accelerate."
        ) from exc

    if _PIPELINE is None:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        _PIPELINE = AutoPipelineForText2Image.from_pretrained(
            LOCAL_DIFFUSION_MODEL,
            torch_dtype=dtype,
            use_safetensors=True,
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _PIPELINE = _PIPELINE.to(device)
        if device == "cpu":
            _PIPELINE.enable_attention_slicing()

    return _PIPELINE(
        prompt,
        height=512,
        width=768,
        num_inference_steps=20,
        guidance_scale=7.0,
    ).images[0]


def generate_image(prompt: str, filename: str | None = None) -> GeneratedImage:
    """Generate a comic panel illustration and return GeneratedImage with path and Base64."""
    if not filename:
        filename = f"{sanitize_filename(prompt)}.png"
    elif not filename.lower().endswith(".png"):
        filename = f"{filename}.png"

    image: Image.Image | None = None

    # 1. Hugging Face if token is configured
    if (IMAGE_PROVIDER == "hf" or (IMAGE_PROVIDER == "auto" and HF_TOKEN)) and HF_TOKEN:
        try:
            image = _hf_image(prompt)
        except Exception:
            image = None

    # 2. Local PyTorch Diffusers if requested
    if image is None and IMAGE_PROVIDER == "diffusers":
        try:
            image = _diffusers_image(prompt)
        except Exception:
            image = None

    # 3. Cloud AI Image Generator (Free Flux/Stable Diffusion)
    if image is None and IMAGE_PROVIDER in {"auto", "hf", "cloud", "free"}:
        try:
            image = _cloud_ai_image(prompt)
        except Exception:
            image = None

    # 4. Fallback to styled demo canvas if offline
    if image is None:
        return _demo_image(prompt, filename)

    path = PANELS_DIR / filename
    try:
        image.save(path, format="PNG")
    except Exception:
        pass

    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"
    return GeneratedImage(path=str(path), data_url=data_url, filename=filename)
