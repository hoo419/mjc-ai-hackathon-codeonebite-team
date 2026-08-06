from pathlib import Path
from zipfile import ZipFile

import pdfplumber


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "MJC_AI_Campus_Agent_해커톤_보고서.pdf"
DECK_PDF = ROOT / "MJC_AI_Campus_Agent_5분_발표자료.pdf"
DECK = ROOT / "MJC_AI_Campus_Agent_5분_발표자료.pptx"
SCRIPT = ROOT / "MJC_AI_Campus_Agent_5분_발표대본.md"
DOCX = ROOT / "MJC_AI_Campus_Agent_해커톤_보고서.docx"


def main() -> None:
    for file in [REPORT, DECK_PDF, DECK, SCRIPT, DOCX]:
        assert file.exists() and file.stat().st_size > 0, f"missing: {file}"
        print(file.name, file.stat().st_size)

    with pdfplumber.open(REPORT) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        assert len(pdf.pages) == 12
        for token in [
            "전자공학과 임채호",
            "AI게임소프트웨어학과 조영남",
            "github.com/hoo419/mjc-ai-hackathon-codeonebite-team",
            "246",
            "516",
            "14개 서비스",
        ]:
            assert token in text, token
        print("report_pages", len(pdf.pages), "report_tokens_ok")

    with pdfplumber.open(DECK_PDF) as pdf:
        assert len(pdf.pages) == 3
        print("deck_pdf_pages", len(pdf.pages))

    with ZipFile(DECK) as archive:
        slides = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        notes = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
        ]
        assert len(slides) == 3
        assert len(notes) == 3
        notes_xml = "".join(
            archive.read(name).decode("utf-8", "ignore") for name in notes
        )
        assert "[Sources]" in notes_xml
        print("pptx_slides", len(slides), "source_notes", len(notes))

    report_renders = list((ROOT / ".build" / "report-render").glob("page-*.png"))
    deck_renders = list((ROOT / ".build" / "deck-pdf-render").glob("slide-*.png"))
    assert len(report_renders) == 12
    assert len(deck_renders) == 3
    print("render_counts", len(report_renders), len(deck_renders))


if __name__ == "__main__":
    main()
