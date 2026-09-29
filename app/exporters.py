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
    """Compile the full comic panels, artwork, and story into a PDF document."""
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        
        # Header / Title
        pdf.set_font("Helvetica", size=16)
        title_text = panel.get("full_title") or f"Panel {panel['panel']}: {panel['title']}"
        pdf.cell(0, 12, _pdf_safe(title_text), ln=True, align="C")

        # Artwork image placement
        image_path = Path(panel.get("image_path", ""))
        y = 30
        image_rendered = False

        if image_path and image_path.exists():
            try:
                pdf.image(str(image_path), x=15, y=y, w=pdf.w - 30)
                y += 105
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
                pdf.image(img_io, x=15, y=y, w=pdf.w - 30)
                y += 105
                image_rendered = True
            except Exception:
                image_rendered = False

        if not image_rendered:
            pdf.set_y(y)
            pdf.multi_cell(0, 8, _pdf_safe(f"[Image Unavailable: {title_text}]"))
            y += 20

        # Scene description
        pdf.set_y(y)
        if panel.get("scene_description"):
            pdf.set_font("Helvetica", style="I", size=10)
            pdf.multi_cell(0, 6, _pdf_safe(panel["scene_description"]))
            pdf.ln(3)

        # Story text / dialogue / captions
        if panel.get("text"):
            pdf.set_font("Helvetica", size=11)
            pdf.multi_cell(0, 6.5, _pdf_safe(panel["text"]))

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
