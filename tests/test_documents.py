from io import BytesIO

from pypdf import PdfWriter

from src.backend.document_service import process_document


def test_pdf_processing_returns_preview():
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)

    result = process_document("sample.pdf", output.getvalue())
    assert result["status"] == "processed"
    assert result["filename"] == "sample.pdf"
    assert result["characters_extracted"] == 0