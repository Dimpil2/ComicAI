from __future__ import annotations

from datetime import datetime
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

        image_path = Path(panel["image_path"])
        y = 30
        if image_path.exists():
            pdf.image(str(image_path), x=10, y=y, w=pdf.w - 20)
            y += 95
        else:
            pdf.set_y(y)
            pdf.multi_cell(0, 8, _pdf_safe(f"Image missing: {image_path}"))
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
    pdf.output(str(output_path))
    return str(output_path)
