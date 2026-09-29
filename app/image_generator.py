from __future__ import annotations

import base64
import re
from io import BytesIO
from pathlib import Path

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
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def _demo_image(prompt: str, filename: str) -> GeneratedImage:
    image = Image.new("RGB", (768, 512), (235, 242, 250))
    draw = ImageDraw.Draw(image)
    title_font = _load_font(28)
    body_font = _load_font(18)
    draw.rounded_rectangle((30, 30, 738, 482), radius=24, outline=(45, 72, 100), width=4)
    draw.text((55, 55), "ComicCraft Demo Panel", font=title_font, fill=(30, 42, 55))
    text = prompt[:420]
    draw.multiline_text((55, 120), text, font=body_font, fill=(50, 60, 70), spacing=8)
    draw.text((55, 420), "Set IMAGE_PROVIDER=hf or diffusers for AI images.", font=body_font, fill=(70, 80, 95))
    
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


def _hf_image(prompt: str):
    from huggingface_hub import InferenceClient

    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN is missing for IMAGE_PROVIDER=hf.")
    client = InferenceClient(api_key=HF_TOKEN, provider="auto")
    return client.text_to_image(prompt=prompt, model=HF_IMAGE_MODEL)


def _diffusers_image(prompt: str):
    global _PIPELINE
    try:
        import torch
        from diffusers import AutoPipelineForText2Image
    except ImportError as exc:
        raise RuntimeError(
            "Diffusers mode needs torch, diffusers, transformers, and accelerate. "
            "Install them from requirements-local-image.txt."
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
    """Generate a comic panel image and return its static file path & base64 data URI."""
    if not filename:
        filename = f"{sanitize_filename(prompt)}.png"
    elif not filename.lower().endswith(".png"):
        filename = f"{filename}.png"

    if DEMO_MODE or IMAGE_PROVIDER == "demo":
        return _demo_image(prompt, filename)

    if IMAGE_PROVIDER == "hf":
        image = _hf_image(prompt)
    elif IMAGE_PROVIDER == "diffusers":
        image = _diffusers_image(prompt)
    else:
        raise RuntimeError(
            "IMAGE_PROVIDER must be one of: demo, hf, diffusers."
        )

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
