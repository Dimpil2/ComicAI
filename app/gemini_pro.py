from __future__ import annotations

from .config import DEMO_MODE, GEMINI_STORY_MODEL
from .gemini_client import generate_text


def _demo_story(outline: list[dict]) -> str:
    chunks = []
    for panel in outline:
        n = panel["panel"]
        title = panel["title"]
        desc = panel["scene_description"]
        chunks.append(
            f"Panel {n}: {title}\n"
            f"CAPTION: The story moves forward as the scene unfolds.\n"
            f"NARRATION: {desc}\n"
            f"DIALOGUE: Hero: \"I have to keep going.\"\n"
            f"DIALOGUE: Friend: \"We can do this together!\""
        )
    return "\n\n".join(chunks)


def generate_story(outline: list[dict]) -> str:
    """Expand the five-panel outline into narration and dialogue."""
    if DEMO_MODE:
        return _demo_story(outline)

    formatted_outline = "\n".join(
        f"{i + 1}. {item['title']} — {item['scene_description']}"
        for i, item in enumerate(outline)
    )

    prompt = f"""
You are a comic book writer.

Given the following 5-panel outline, write a cohesive comic story.

{formatted_outline}

Requirements:
- Keep exactly five panel sections.
- Start each section with 'Panel N: <title>'.
- Include a short CAPTION line.
- Include NARRATION describing action and emotion.
- Include concise DIALOGUE lines for the characters.
- Keep the panels self-contained but connected as one story.
- Use the tone and visual details from the outline.

Return plain text only. No markdown code fences.
""".strip()
    return generate_text(prompt, GEMINI_STORY_MODEL, json_mode=False)
