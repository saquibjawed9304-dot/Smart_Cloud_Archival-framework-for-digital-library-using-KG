from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from src.backend.main import app


client = TestClient(app)


def test_health_and_frontend_are_available():
    assert client.get("/api/health").status_code == 200
    response = client.get("/")
    assert response.status_code == 200
    assert "Smart Archival" in response.text


def test_books_and_graph_contracts():
    books = client.get("/api/books")
    graph = client.get("/api/graph")
    assert books.status_code == 200
    assert len(books.json()) == 12
    assert graph.status_code == 200
    assert graph.json()["nodes"]
    assert graph.json()["edges"]


def test_book_has_readable_and_downloadable_blank_pdf():
    response = client.get("/api/books")
    book = response.json()[0]
    assert book["read_url"].endswith(f"/api/books/{book['id']}/pdf")

    readable = client.get(book["read_url"])
    downloadable = client.get(book["download_url"])
    assert readable.status_code == 200
    assert readable.headers["content-type"].startswith("application/pdf")
    assert downloadable.status_code == 200
    assert "attachment" in downloadable.headers["content-disposition"]


def test_unknown_book_graph_returns_not_found():
    response = client.get("/api/graph/unknown")
    assert response.status_code == 404


def test_invalid_upload_is_rejected():
    response = client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 422


def test_uploaded_pdf_is_listed():
    pdf = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(pdf)
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("empty-fixture.pdf", pdf.getvalue(), "application/pdf")},
    )
    assert upload.status_code == 200
    uploaded = upload.json()
    assert client.get(uploaded["read_url"]).status_code == 200
    assert "attachment" in client.get(uploaded["download_url"]).headers["content-disposition"]

    deleted = client.delete(f"/api/documents/{uploaded['document_id']}")
    assert deleted.status_code == 200
    assert client.get(uploaded["read_url"]).status_code == 404

    documents = client.get("/api/documents")
    assert documents.status_code == 200
    assert any(document["filename"] == "empty-fixture.pdf" for document in documents.json())