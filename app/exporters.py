from __future__ import annotations

import base64
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fpdf import FPDF

from .config import EXPORTS_DIR


def _pdf_safe(text: str) -> str:
    # Built-in Helvetica is reliable on every machine, so strip unsupported
    # Unicode characters instead of failing during PDF export.
    return text.encode("latin-1", errors="replace").decode("latin-1")


def save_pdf(layout: list[dict]) -> str:
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", size=16)
        pdf.cell(0, 10, _pdf_safe(f"Panel {panel['panel']}: {panel['title']}"), ln=True, align="C")

        image_path = Path(panel.get("image_path", ""))
        y = 30
        image_rendered = False

        if image_path and image_path.exists():
            try:
                pdf.image(str(image_path), x=10, y=y, w=pdf.w - 20)
                y += 95
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
                pdf.image(img_io, x=10, y=y, w=pdf.w - 20)
                y += 95
                image_rendered = True
            except Exception:
                image_rendered = False

        if not image_rendered:
            pdf.set_y(y)
            pdf.multi_cell(0, 8, _pdf_safe(f"Image unavailable: {panel.get('title', '')}"))
            y += 20

        pdf.set_y(y)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 7, _pdf_safe(panel.get("scene_description", "")))
        pdf.ln(3)
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, _pdf_safe(panel.get("text", "")))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    output_path = EXPORTS_DIR / filename
    try:
        pdf.output(str(output_path))
    except Exception:
        # Safe fallback in read-only environments
        tmp_fallback = Path(tempfile.gettempdir()) / filename
        pdf.output(str(tmp_fallback))
        output_path = tmp_fallback

    return str(output_path)
