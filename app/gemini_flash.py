from __future__ import annotations

import json

from .config import DEMO_MODE, GEMINI_OUTLINE_MODEL
from .gemini_client import generate_text


def _demo_outline(user_prompt: str) -> list[dict]:
    # Keeps the full application testable before API keys are configured.
    titles = [
        "The Beginning",
        "Into the Unknown",
        "A Sudden Challenge",
        "The Turning Point",
        "A New Dawn",
    ]
    results = []
    for i, title in enumerate(titles, start=1):
        results.append(
            {
                "panel": i,
                "title": title,
                "scene_description": (
                    f"A comic-book scene for panel {i}, continuing the story idea: {user_prompt}."
                ),
                "image_prompt": (
                    f"comic book illustration, panel {i}, {user_prompt}, cinematic composition, "
                    "expressive characters, detailed environment, vivid lighting, clean line art"
                ),
            }
        )
    return results


def generate_outline(user_prompt: str) -> list[dict]:
    """Generate a strictly structured 5-panel comic outline."""
    if DEMO_MODE and not user_prompt:
        raise ValueError("Story prompt cannot be empty.")

    if DEMO_MODE:
        return _demo_outline(user_prompt)

    prompt = f"""
You are a professional AI comic planner.

Create a strictly formatted JSON array containing exactly 5 comic panel descriptions
for this story idea:

STORY: {user_prompt}

Each object MUST contain exactly these keys:
- panel (integer 1-5)
- title (string)
- scene_description (string)
- image_prompt (string)

The image_prompt must be suitable for a comic-style text-to-image model and should
include visual composition, characters, setting, mood, and art direction.

Respond ONLY with valid JSON. Do not wrap it in markdown fences.
""".strip()

    raw = generate_text(prompt, GEMINI_OUTLINE_MODEL, json_mode=True)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(cleaned)

    if not isinstance(data, list) or len(data) != 5:
        raise ValueError("Gemini outline is not a 5-panel list.")

    required = {"panel", "title", "scene_description", "image_prompt"}
    normalized = []
    for index, panel in enumerate(data, start=1):
        if not isinstance(panel, dict) or not required.issubset(panel):
            raise ValueError(f"Invalid panel structure at panel {index}.")
        normalized.append(
            {
                "panel": index,
                "title": str(panel["title"]).strip(),
                "scene_description": str(panel["scene_description"]).strip(),
                "image_prompt": str(panel["image_prompt"]).strip(),
            }
        )
    return normalized
