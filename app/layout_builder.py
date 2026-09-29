from __future__ import annotations
import re


def _extract_panel_story(full_story: str, panel_num: int) -> str:
    """Extract story text specifically for a given panel number."""
    # Pattern looking for Panel N: ... up to next Panel or end
    pattern = rf"(?i)(?:^|\n)\s*Panel\s*{panel_num}\s*[:\-].*?\n(.*?)(?=\n\s*Panel\s*\d+\s*[:\-]|\Z)"
    match = re.search(pattern, full_story, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback: split by 'Panel '
    chunks = [c.strip() for c in re.split(r"(?i)\bpanel\s+\d+[:\s-]*", full_story) if c.strip()]
    if 1 <= panel_num <= len(chunks):
        lines = chunks[panel_num - 1].splitlines()
        return "\n".join(lines).strip()
    return ""


def _clean_title(raw_title: str, idx: int) -> str:
    t = str(raw_title).strip()
    t = re.sub(r"(?i)^panel\s*\d+[:\s-]*", "", t).strip()
    return t or f"Scene {idx}"


def build_comic_layout(images: list, full_story: str, outline: list[dict]) -> list[dict]:
    """Assemble individual comic panel elements into a cohesive structured layout."""
    layout = []

    for idx, (image_info, panel_info) in enumerate(zip(images, outline), start=1):
        raw_title = panel_info.get("title", f"Scene {idx}")
        clean_title = _clean_title(raw_title, idx)
        story_text = _extract_panel_story(full_story, idx)

        # Fallback if empty
        if not story_text:
            story_text = (
                f"**CAPTION:** The journey unfolds into new horizons...\n"
                f"**NARRATION:** Actions speak louder as courage takes flight.\n"
                f"**DIALOGUE:** Hero: \"We are ready for what comes next.\""
            )

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
                "text": story_text,
                "scene_description": str(panel_info.get("scene_description", "")).strip(),
                "image_prompt": str(panel_info.get("image_prompt", "")).strip(),
            }
        )
    return layout
