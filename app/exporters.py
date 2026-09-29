from __future__ import annotations

import base64
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fpdf import FPDF

from .config import EXPORTS_DIR


def _pdf_safe(text: str) -> str:
    """Sanitize text for standard PDF Helvetica font encoding."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def save_pdf(layout: list[dict]) -> str:
    """Compile the full comic panels, artwork, and story into a beautifully structured PDF."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    for panel in layout:
        pdf.add_page()
        pdf.set_margins(18, 15, 18)

        # 1. Panel Header (Title)
        pdf.set_font("Helvetica", size=16)
        pdf.set_text_color(15, 23, 42)
        title_text = panel.get("full_title") or f"Panel {panel.get('panel', 1)}: {panel.get('title', 'Scene')}"
        pdf.set_y(15)
        pdf.cell(0, 10, _pdf_safe(title_text), ln=True, align="C")

        # 2. Artwork Image (Explicitly bounded: 150mm width x 95mm height)
        y_image = 27
        img_w = 150
        img_h = 95
        x_image = (pdf.w - img_w) / 2  # Centered

        image_rendered = False
        image_path = Path(panel.get("image_path", ""))

        if image_path and image_path.exists():
            try:
                pdf.image(str(image_path), x=x_image, y=y_image, w=img_w, h=img_h)
                image_rendered = True
            except Exception:
                image_rendered = False

        if not image_rendered and panel.get("image_data_url"):
            try:
                data_str = panel["image_data_url"]
                if "," in data_str:
                    data_str = data_str.split(",", 1)[1]
                img_bytes = base64.b64decode(data_str)
                img_io = BytesIO(img_bytes)
                pdf.image(img_io, x=x_image, y=y_image, w=img_w, h=img_h)
                image_rendered = True
            except Exception:
                image_rendered = False

        if not image_rendered:
            pdf.set_y(y_image + 35)
            pdf.set_font("Helvetica", style="I", size=11)
            pdf.set_text_color(100, 116, 139)
            pdf.cell(0, 10, _pdf_safe(f"[Artwork Illustration: {panel.get('title', '')}]"), align="C")

        # 3. Scene Description (Positioned safely below the image at y = 130mm)
        y_text_start = y_image + img_h + 8
        pdf.set_y(y_text_start)

        if panel.get("scene_description"):
            pdf.set_font("Helvetica", style="I", size=10.5)
            pdf.set_text_color(71, 85, 105)
            pdf.multi_cell(0, 5.5, _pdf_safe(panel["scene_description"].strip()))
            pdf.ln(3)

        # 4. Captions, Narration & Dialogue
        story_text = panel.get("text", "").strip()
        if story_text:
            pdf.set_font("Helvetica", size=11)
            pdf.set_text_color(30, 41, 59)
            
            lines = story_text.splitlines()
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    continue
                # Clean markdown asterisks for clean PDF typography
                clean_display = clean_line.replace("**", "").replace("##", "")
                pdf.multi_cell(0, 6.5, _pdf_safe(clean_display))
                pdf.ln(1)

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    output_path = EXPORTS_DIR / filename
    try:
        pdf.output(str(output_path))
    except Exception:
        tmp_fallback = Path(tempfile.gettempdir()) / filename
        pdf.output(str(tmp_fallback))
        output_path = tmp_fallback

    return str(output_path)
