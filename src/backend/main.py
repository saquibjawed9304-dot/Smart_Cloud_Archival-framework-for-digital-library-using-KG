from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import ALLOWED_ORIGINS, APP_NAME, APP_VERSION, DATA_BACKEND, FRONTEND_DIR
from .data_store import (
    load_books,
    search_books,
    get_statistics
)
from .graph_service import (
    build_graph,
    get_book_graph
)
from .document_service import (
    delete_uploaded_document,
    ensure_book_pdf,
    list_documents,
    process_document,
    uploaded_document_path,
)
from .document_service import DocumentValidationError
from .models import Book, DocumentResult, DocumentSummary, GraphResponse, SearchResponse, Statistics


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


def book_payload(book):
    return {
        **book,
        "pdf_status": "blank placeholder",
        "read_url": f"/api/books/{book['id']}/pdf",
        "download_url": f"/api/books/{book['id']}/download",
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
        "data_backend": DATA_BACKEND,
    }


@app.get("/api/books", response_model=list[Book])
def books():
    return [book_payload(book) for book in load_books()]


@app.get("/api/search", response_model=SearchResponse)
def search(
    q: str = Query(default="")
):
    results = search_books(q)

    return {
        "query": q,
        "total": len(results),
        "results": [book_payload(book) for book in results]
    }


@app.get("/api/statistics", response_model=Statistics)
def statistics():
    return get_statistics()


@app.get("/api/graph", response_model=GraphResponse)
def graph():
    return build_graph()


@app.get("/api/graph/{book_id}", response_model=GraphResponse)
def book_graph(book_id: str):
    return get_book_graph(book_id)


@app.post("/api/documents/upload", response_model=DocumentResult)
async def upload_document(
    file: UploadFile = File(...)
):

    content = await file.read()

    try:
        result = process_document(file.filename or "", content)
    except DocumentValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return result


@app.get("/api/documents", response_model=list[DocumentSummary])
def documents():
    return list_documents()


@app.get("/api/books/{book_id}/pdf")
def read_book_pdf(book_id: str):
    if not any(book["id"] == book_id for book in load_books()):
        raise HTTPException(status_code=404, detail="Book not found")
    try:
        file_path = ensure_book_pdf(book_id)
    except DocumentValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"{book_id}.pdf",
        content_disposition_type="inline",
    )


@app.get("/api/books/{book_id}/download")
def download_book_pdf(book_id: str):
    if not any(book["id"] == book_id for book in load_books()):
        raise HTTPException(status_code=404, detail="Book not found")
    file_path = ensure_book_pdf(book_id)
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"{book_id}_empty.pdf",
        content_disposition_type="attachment",
    )


@app.get("/api/documents/{document_id}/read")
def read_document(document_id: str):
    try:
        file_path = uploaded_document_path(document_id)
    except (DocumentValidationError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Uploaded PDF not found") from error
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=file_path.name,
        content_disposition_type="inline",
    )


@app.get("/api/documents/{document_id}/download")
def download_document(document_id: str):
    try:
        file_path = uploaded_document_path(document_id)
    except (DocumentValidationError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Uploaded PDF not found") from error
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=file_path.name.split("_", 1)[-1],
        content_disposition_type="attachment",
    )


@app.delete("/api/documents/{document_id}")
def delete_document(document_id: str):
    try:
        delete_uploaded_document(document_id)
    except (DocumentValidationError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Uploaded PDF not found") from error
    return {"status": "deleted", "document_id": document_id}


@app.get("/api")
def root():
    return {
        "message": "Smart Cloud Archival Digital Library API",
        "docs": "/docs"
    }


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")