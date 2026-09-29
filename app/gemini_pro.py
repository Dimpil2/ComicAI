from __future__ import annotations

from .config import DEMO_MODE, GEMINI_STORY_MODEL
from .gemini_client import generate_text


def _demo_story(outline: list[dict]) -> str:
    """Generates rich comic story dialogue, caption, and narration for demo mode."""
    captions = [
        "Whispers carried on the wind, tales of magic and mystery...",
        "Every step brought deeper shadows and ancient secrets...",
        "A sudden luminescence broke the stillness of the horizon...",
        "Courage tested in the moment of greatest uncertainty...",
        "The light breaks through, signaling a brand new chapter...",
    ]
    
    chunks = []
    for i, panel in enumerate(outline):
        n = panel["panel"]
        title = panel["title"]
        desc = panel["scene_description"]
        caption = captions[i % len(captions)]
        
        chunks.append(
            f"{title}\n"
            f"**CAPTION:** {caption}\n"
            f"**NARRATION:** {desc}\n"
            f"**DIALOGUE:** Hero: \"There's no turning back now. We have to see what lies beyond.\"\n"
            f"**DIALOGUE:** Companion: \"I'm with you, all the way!\""
        )
    return "\n\n".join(chunks)


def generate_story(outline: list[dict]) -> str:
    """Expand the five-panel outline into narration, captions, and dialogue."""
    if DEMO_MODE:
        return _demo_story(outline)

    formatted_outline = "\n".join(
        f"{item['title']} — {item['scene_description']}"
        for item in outline
    )

    prompt = f"""
You are a professional comic book writer.

Given the following 5-panel outline, write an engaging comic story:

{formatted_outline}

Guidelines:
- Keep exactly five panel sections.
- Start each section with 'Panel N: <Title>'.
- Include a **CAPTION:** line setting atmospheric context.
- Include a **NARRATION:** line detailing character action and feelings.
- Include **DIALOGUE:** lines with character names and quotes.
- Keep the narrative cohesive, lively, and aligned with comic book conventions.

Return plain text only. No markdown code fences.
""".strip()
    return generate_text(prompt, GEMINI_STORY_MODEL, json_mode=False)
