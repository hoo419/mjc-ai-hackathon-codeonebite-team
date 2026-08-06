from pathlib import Path

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "MJC_AI_Campus_Agent_5분_발표자료.pdf"
IMAGES = sorted((ROOT / ".build" / "deck-render").glob("slide-*.png"))


def main() -> None:
    width, height = 13.333 * inch, 7.5 * inch
    pdf = canvas.Canvas(str(OUT), pagesize=(width, height), pageCompression=1)
    for image in IMAGES:
        pdf.drawImage(str(image), 0, 0, width=width, height=height, preserveAspectRatio=True, mask="auto")
        pdf.showPage()
    pdf.save()
    print(OUT)


if __name__ == "__main__":
    main()
