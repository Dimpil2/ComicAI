from __future__ import annotations

import json

from .config import DEMO_MODE, GEMINI_OUTLINE_MODEL
from .gemini_client import generate_text


def _demo_outline(user_prompt: str) -> list[dict]:
    """Generates an engaging, contextual 5-panel outline for demo and test modes."""
    # Context-aware panel titles and progression
    panels_data = [
        (
            "The Threshold of Adventure",
            f"The journey begins as the scene sets the atmosphere for: {user_prompt}.",
            f"Comic book illustration, wide establishing shot, {user_prompt}, cinematic composition, vivid lighting, detailed setting, clean line art."
        ),
        (
            "Into the Unknown",
            f"The main character steps deeper into the setting, noticing unfamiliar details and rising anticipation.",
            f"Comic book panel, medium shot, character exploring the environment, atmospheric lighting, detailed background, dynamic angle."
        ),
        (
            "A Sudden Discovery",
            f"A surprising anomaly or mysterious encounter challenges the path ahead and heightens the stakes.",
            f"Comic illustration, dramatic close-up, glowing elements, expressive character reaction, high contrast shadows, comic book style."
        ),
        (
            "The Turning Point",
            f"Facing the central revelation, courage and quick thinking turn uncertainty into action.",
            f"Dynamic action comic panel, intense color palette, expressive hero pose, impactful lighting, detailed scene."
        ),
        (
            "A New Dawn",
            f"The immediate challenge is resolved, leading to a satisfying conclusion and the promise of future adventures.",
            f"Heroic resolution panel, warm golden hour lighting, wide cinematic frame, triumphant character expression, masterwork art."
        ),
    ]

    results = []
    for i, (title, desc, img_prompt) in enumerate(panels_data, start=1):
        results.append(
            {
                "panel": i,
                "title": f"Panel {i}: {title}",
                "scene_description": desc,
                "image_prompt": img_prompt,
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
        
        # Ensure clean title without double 'Panel N:' prefixes
        raw_title = str(panel["title"]).strip()
        if raw_title.lower().startswith(f"panel {index}"):
            clean_title = raw_title
        else:
            clean_title = f"Panel {index}: {raw_title}"

        normalized.append(
            {
                "panel": index,
                "title": clean_title,
                "scene_description": str(panel["scene_description"]).strip(),
                "image_prompt": str(panel["image_prompt"]).strip(),
            }
        )
    return normalized
