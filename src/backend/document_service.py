from pathlib import Path
import re
from uuid import uuid4
from pypdf import PdfReader, PdfWriter

from .config import MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR


class DocumentValidationError(ValueError):
    pass


def save_document(filename: str, content: bytes):
    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise DocumentValidationError("Only PDF documents are accepted")
    if not content or len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise DocumentValidationError(
            f"PDF must be between 1 byte and {MAX_UPLOAD_SIZE_BYTES} bytes"
        )
    if not content.startswith(b"%PDF-"):
        raise DocumentValidationError("The uploaded file is not a valid PDF")

    safe_name = Path(filename).name
    destination = UPLOAD_DIR / f"{uuid4().hex}_{safe_name}"

    with open(destination, "wb") as file:
        file.write(content)

    return destination


def extract_text(file_path: Path):
    reader = PdfReader(str(file_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text.strip()


def process_document(filename: str, content: bytes):
    file_path = save_document(filename, content)
    try:
        text = extract_text(file_path)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise DocumentValidationError("The PDF could not be read")

    return {
        "status": "processed",
        "document_id": file_path.stem.split("_", 1)[0],
        "filename": filename,
        "size_bytes": len(content),
        "characters_extracted": len(text),
        "text_preview": text[:1000],
        "read_url": f"/api/documents/{file_path.stem.split('_', 1)[0]}/read",
        "download_url": f"/api/documents/{file_path.stem.split('_', 1)[0]}/download",
    }


def list_documents():
    documents = []
    for file_path in sorted(UPLOAD_DIR.glob("*.pdf"), key=lambda path: path.stat().st_mtime, reverse=True):
        if file_path.name.startswith("book_"):
            continue
        document_id, _, original_name = file_path.stem.partition("_")
        documents.append({
            "id": document_id or file_path.stem,
            "filename": original_name or file_path.name,
            "size_bytes": file_path.stat().st_size,
            "status": "stored",
            "read_url": f"/api/documents/{document_id}/read",
            "download_url": f"/api/documents/{document_id}/download",
        })
    return documents


def ensure_book_pdf(book_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9-]+", book_id):
        raise DocumentValidationError("Invalid book identifier")

    file_path = UPLOAD_DIR / f"book_{book_id}_empty.pdf"
    if not file_path.exists():
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        with file_path.open("wb") as file:
            writer.write(file)
    return file_path


def uploaded_document_path(document_id: str) -> Path:
    if not re.fullmatch(r"[a-f0-9]{32}", document_id):
        raise DocumentValidationError("Invalid document identifier")

    matches = list(UPLOAD_DIR.glob(f"{document_id}_*.pdf"))
    if not matches:
        raise FileNotFoundError("Document not found")
    return matches[0]


def delete_uploaded_document(document_id: str) -> None:
    file_path = uploaded_document_path(document_id)
    file_path.unlink()