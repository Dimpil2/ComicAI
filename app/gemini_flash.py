from __future__ import annotations

import json
import re

from .config import DEMO_MODE, GEMINI_OUTLINE_MODEL
from .gemini_client import generate_text


def _demo_outline(user_prompt: str) -> list[dict]:
    """Generates an engaging, contextual 5-panel outline matching project document scenarios."""
    # Extract character name if present in prompt
    char_match = re.search(r"main character is ([^.]+)", user_prompt, re.IGNORECASE)
    char_name = char_match.group(1).strip() if char_match else "Free"

    panels = [
        {
            "panel": 1,
            "title": "The Forest's Edge",
            "scene_description": f"{char_name}, a red fox with intelligent eyes, stands at the edge of a dark, imposing forest. Sunlight barely penetrates the dense canopy. He looks apprehensive but determined.",
            "image_prompt": f"Realistic painting of a red fox, {char_name}, standing at the edge of a dark, mysterious forest. Dramatic lighting, sunlight barely penetrating the trees. Focus on the fox's determined expression.",
        },
        {
            "panel": 2,
            "title": "Into the Deep Woods",
            "scene_description": f"{char_name} cautiously enters the forest, the path barely visible beneath twisted branches and overgrown foliage. An unnatural silence hangs in the air.",
            "image_prompt": f"Red fox exploring deeper into a dense mystical forest, twisted ancient oak trees, lush mossy ground, ethereal green atmospheric haze, cinematic composition.",
        },
        {
            "panel": 3,
            "title": "A Strange Luminescence",
            "scene_description": f"Deep in the woods, {char_name} discovers a giant ancient willow tree pulsing with soft turquoise light. Floating motes of starlight dance around its roots.",
            "image_prompt": f"Magical ancient willow tree glowing with bioluminescent turquoise light in a dark forest, tiny floating starlight orbs, mystical atmosphere, vibrant colors.",
        },
        {
            "panel": 4,
            "title": "The Ancient Guardian",
            "scene_description": f"A glowing celestial stag emerges from behind the willow tree, gazing down at {char_name} with ancient wisdom and bowing its radiant antlers.",
            "image_prompt": f"A majestic glowing spirit stag with radiant crystal antlers appearing in front of a brave red fox, enchanting moonlight, high detail comic art style.",
        },
        {
            "panel": 5,
            "title": "The Journey Ahead",
            "scene_description": f"{char_name} accepts a glowing leaf amulet from the guardian, stepping forward into the moonlit horizon as the chosen protector of the enchanted forest.",
            "image_prompt": f"Heroic shot of red fox wearing a glowing celestial amulet, standing on a hill looking toward a sunlit magical horizon, triumphant and inspiring scene.",
        },
    ]
    return panels


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
- title (string, e.g. "The Forest's Edge")
- scene_description (string, a short atmospheric descriptive paragraph for the scene)
- image_prompt (string, detailed visual prompt for image generation)

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
        
        # Clean title to avoid 'Panel N:' repetition
        raw_title = str(panel["title"]).strip()
        raw_title = re.sub(r"(?i)^panel\s*\d+[:\s-]*", "", raw_title).strip()

        normalized.append(
            {
                "panel": index,
                "title": raw_title or f"Scene {index}",
                "scene_description": str(panel["scene_description"]).strip(),
                "image_prompt": str(panel["image_prompt"]).strip(),
            }
        )
    return normalized
