from __future__ import annotations

import re

from .config import DEMO_MODE, GEMINI_STORY_MODEL
from .gemini_client import generate_text


def _demo_story(outline: list[dict]) -> str:
    """Generates structured comic narration, caption, and dialogue for demo mode."""
    demos = [
        (
            "**CAPTION:** Whispers carried on the wind, tales of magic and mystery. Tales of the Whispering Woods...\n"
            "**NARRATION:** Free, the bravest fox this side of Silverstream, stood at the threshold. The ancient trees loomed like watchful giants, their shadows a daunting promise.\n"
            "**DIALOGUE:** Free: \"There's no turning back now. The forest holds the answers I seek.\""
        ),
        (
            "**CAPTION:** With every step, the outside world faded into twilight green...\n"
            "**NARRATION:** He pressed on cautiously, keen senses tuned to the rustle of unseen leaves. The air grew thick with ancient enchantments.\n"
            "**DIALOGUE:** Free: \"Steady now... one step at a time.\""
        ),
        (
            "**CAPTION:** Out of the creeping darkness, an ethereal light bloomed...\n"
            "**NARRATION:** A soft turquoise luminescence pulsed from the heart of the great willow tree, casting dancing reflections across the ancient moss.\n"
            "**DIALOGUE:** Free: \"Incredible... the legends were truly real!\""
        ),
        (
            "**CAPTION:** An encounter not of fear, but of sacred destiny...\n"
            "**NARRATION:** The radiant guardian bowed its glowing crystal antlers, acknowledging the pure courage residing in the small traveler.\n"
            "**DIALOGUE:** Guardian: \"You who walk with an untamed heart, the woods have awaited your arrival.\""
        ),
        (
            "**CAPTION:** A journey begun in curiosity, now bound in honor...\n"
            "**NARRATION:** Wearing the celestial amulet, Free stepped forward onto the sunlit trail, ready to protect the realm with every stride.\n"
            "**DIALOGUE:** Free: \"I will protect this enchanted land with my life!\""
        ),
    ]

    chunks = []
    for i, panel in enumerate(outline):
        n = panel["panel"]
        title = panel["title"]
        story_body = demos[i % len(demos)]
        chunks.append(f"Panel {n}: {title}\n{story_body}")
    return "\n\n".join(chunks)


def generate_story(outline: list[dict]) -> str:
    """Expand the five-panel outline into clean, structured narration, captions, and dialogue."""
    if DEMO_MODE:
        return _demo_story(outline)

    formatted_outline = "\n".join(
        f"Panel {item['panel']}: {item['title']} — {item['scene_description']}"
        for item in outline
    )

    prompt = f"""
You are a professional comic book writer.

Given the following 5-panel outline, write the narration, captions, and dialogue for each panel:

{formatted_outline}

Format each panel EXACTLY like this:
Panel N: <Title>
**CAPTION:** <Atmospheric caption describing environment or lore>
**NARRATION:** <Action and character thoughts>
**DIALOGUE:** <Character Name>: "<Spoken dialogue line>"

Guidelines:
- Keep exactly 5 panel sections numbered Panel 1 through Panel 5.
- Do NOT repeat the scene description inside narration.
- Keep the dialogue concise, punchy, and expressive.

Return plain text only without markdown code fences.
""".strip()
    return generate_text(prompt, GEMINI_STORY_MODEL, json_mode=False)
