from pathlib import Path
from pypdf import PdfReader

from .config import UPLOAD_DIR


def save_document(filename: str, content: bytes):
    safe_name = Path(filename).name

    destination = UPLOAD_DIR / safe_name

    with open(destination, "wb") as file:
        file.write(content)

    return destination


def extract_text(file_path: Path):
    if file_path.suffix.lower() != ".pdf":
        return ""

    try:
        reader = PdfReader(str(file_path))

        text = ""

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

        return text.strip()

    except Exception as error:
        return f"Text extraction failed: {error}"


def process_document(filename: str, content: bytes):
    file_path = save_document(filename, content)

    text = extract_text(file_path)

    return {
        "filename": filename,
        "path": str(file_path),
        "characters_extracted": len(text),
        "text_preview": text[:1000]
    }