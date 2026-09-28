from __future__ import annotations

from pathlib import Path

from app.config import DEMO_MODE, IMAGE_PROVIDER
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf


assert DEMO_MODE or IMAGE_PROVIDER != "demo", "Set DEMO_MODE=true for the local smoke test."

prompt = "A curious fox finds a glowing doorway in an old forest."
outline = generate_outline(prompt)
assert len(outline) == 5
story = generate_story(outline)
images = [generate_image(p["image_prompt"], f"smoke_{p['panel']}.png") for p in outline]
layout = build_comic_layout(images, story, outline)
pdf = save_pdf(layout)

print("Smoke test passed")
print("Panels:", len(images))
print("PDF:", Path(pdf).resolve())
