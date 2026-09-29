from __future__ import annotations
import re


def _split_story(story: str) -> list[str]:
    pieces = [p.strip() for p in re.split(r"(?i)\bpanel\s+\d+[:\s]*", story) if p.strip()]
    return pieces


def _story_for_panel(panel_text: str) -> str:
    lines = [line.strip() for line in panel_text.splitlines() if line.strip()]
    if lines and re.match(r"(?i)^panel\s+\d+", lines[0]):
        lines = lines[1:]
    return "\n".join(lines).strip()


def _clean_title(raw_title: str, idx: int) -> str:
    t = raw_title.strip()
    prefix = f"panel {idx}:"
    if t.lower().startswith(prefix):
        return t[len(prefix):].strip()
    prefix2 = f"panel {idx}"
    if t.lower().startswith(prefix2):
        return t[len(prefix2):].lstrip(":- ").strip()
    return t or f"Scene {idx}"


def build_comic_layout(images: list, full_story: str, outline: list[dict]) -> list[dict]:
    story_panels = _split_story(full_story)
    layout = []

    for idx, (image_info, panel_info) in enumerate(zip(images, outline), start=1):
        story_text = story_panels[idx - 1] if idx <= len(story_panels) else ""
        raw_title = str(panel_info.get("title", f"Scene {idx}"))
        clean_title = _clean_title(raw_title, idx)

        if isinstance(image_info, dict):
            image_path = str(image_info.get("path", ""))
            image_data_url = str(image_info.get("data_url", ""))
        else:
            image_path = str(image_info)
            image_data_url = ""

        layout.append(
            {
                "panel": idx,
                "title": clean_title,
                "full_title": f"Panel {idx}: {clean_title}",
                "image_path": image_path,
                "image_data_url": image_data_url,
                "text": _story_for_panel(story_text),
                "scene_description": panel_info.get("scene_description", ""),
                "image_prompt": panel_info.get("image_prompt", ""),
            }
        )
    return layout
