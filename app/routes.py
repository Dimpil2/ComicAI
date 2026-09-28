from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .config import EXPORTS_DIR, TEMPLATES_DIR
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    character_name: str = Field(default="Hero", max_length=100)
    setting: str = Field(default="forest", max_length=100)
    tone: str = Field(default="dramatic", max_length=100)
    style: str = Field(default="comic book", max_length=100)


def _full_prompt(prompt: str, character_name: str, setting: str, tone: str, style: str) -> str:
    return (
        f"{prompt}\n"
        f"The main character is {character_name}. "
        f"The setting is {setting}. "
        f"The tone is {tone}. The art style is {style}."
    )


def _generate_comic(full_prompt: str):
    outline = generate_outline(full_prompt)
    if not isinstance(outline, list) or len(outline) != 5:
        raise ValueError("Invalid outline returned from the AI model.")

    story = generate_story(outline)
    images = [generate_image(panel["image_prompt"], f"panel_{panel['panel']}.png") for panel in outline]
    layout = build_comic_layout(images, story, outline)
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html"
)


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...),
):
    try:
        full_prompt = _full_prompt(prompt, character_name, setting, tone, style)
        layout, pdf_path = _generate_comic(full_prompt)
        pdf_name = Path(pdf_path).name
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_name": pdf_name,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        full_prompt = _full_prompt(
            payload.prompt,
            payload.character_name,
            payload.setting,
            payload.tone,
            payload.style,
        )
        layout, pdf_path = _generate_comic(full_prompt)
        return {
            "message": "Comic generated successfully",
            "layout": layout,
            "pdf_path": f"/download/{Path(pdf_path).name}",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    safe_name = Path(filename).name
    file_path = EXPORTS_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found.")
    return FileResponse(
        path=file_path,
        filename=safe_name,
        media_type="application/pdf",
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_name: str):
    return templates.TemplateResponse(
        "export_success.html",
        {"request": request, "pdf_name": Path(pdf_name).name},
    )


@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, comic art"):
    try:
        image_path = generate_image(prompt, "test_image.png")
        return {"message": "Image generated successfully", "path": image_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
