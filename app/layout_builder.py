from __future__ import annotations


def _split_story(story: str) -> list[str]:
    pieces = [p.strip() for p in story.split("Panel ") if p.strip()]
    return [f"Panel {p}" for p in pieces]


def _story_for_panel(panel_text: str) -> str:
    lines = [line.strip() for line in panel_text.splitlines() if line.strip()]
    if lines and lines[0].lower().startswith("panel "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def build_comic_layout(images: list, full_story: str, outline: list[dict]) -> list[dict]:
    story_panels = _split_story(full_story)
    layout = []

    for idx, (image_info, panel_info) in enumerate(zip(images, outline), start=1):
        story_text = story_panels[idx - 1] if idx <= len(story_panels) else ""
        
        if isinstance(image_info, dict):
            image_path = str(image_info.get("path", ""))
            image_data_url = str(image_info.get("data_url", ""))
        else:
            image_path = str(image_info)
            image_data_url = ""

        layout.append(
            {
                "panel": idx,
                "title": panel_info.get("title", f"Panel {idx}"),
                "image_path": image_path,
                "image_data_url": image_data_url,
                "text": _story_for_panel(story_text),
                "scene_description": panel_info.get("scene_description", ""),
                "image_prompt": panel_info.get("image_prompt", ""),
            }
        )
    return layout
