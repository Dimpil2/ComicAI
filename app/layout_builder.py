from __future__ import annotations


def _split_story(story: str) -> list[str]:
    pieces = [p.strip() for p in story.split("Panel ") if p.strip()]
    return [f"Panel {p}" for p in pieces]


def _story_for_panel(panel_text: str) -> str:
    lines = [line.strip() for line in panel_text.splitlines() if line.strip()]
    if lines and lines[0].lower().startswith("panel "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def build_comic_layout(image_paths: list[str], full_story: str, outline: list[dict]) -> list[dict]:
    story_panels = _split_story(full_story)
    layout = []

    for idx, (image, panel_info) in enumerate(zip(image_paths, outline), start=1):
        story_text = story_panels[idx - 1] if idx <= len(story_panels) else ""
        layout.append(
            {
                "panel": idx,
                "title": panel_info.get("title", f"Panel {idx}"),
                "image_path": image,
                "text": _story_for_panel(story_text),
                "scene_description": panel_info.get("scene_description", ""),
                "image_prompt": panel_info.get("image_prompt", ""),
            }
        )
    return layout
