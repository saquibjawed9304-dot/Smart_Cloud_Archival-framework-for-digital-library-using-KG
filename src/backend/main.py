from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import APP_NAME, APP_VERSION
from .data_store import (
    load_books,
    search_books,
    get_statistics
)
from .graph_service import (
    build_graph,
    get_book_graph
)
from .document_service import process_document


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION
    }


@app.get("/api/books")
def books():
    return load_books()


@app.get("/api/search")
def search(
    q: str = Query(default="")
):
    results = search_books(q)

    return {
        "query": q,
        "total": len(results),
        "results": results
    }


@app.get("/api/statistics")
def statistics():
    return get_statistics()


@app.get("/api/graph")
def graph():
    return build_graph()


@app.get("/api/graph/{book_id}")
def book_graph(book_id: str):
    return get_book_graph(book_id)


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    content = await file.read()

    result = process_document(
        file.filename,
        content
    )

    return {
        "status": "processed",
        **result
    }


@app.get("/api")
def root():
    return {
        "message": "Smart Cloud Archival Digital Library API",
        "docs": "/docs"
    }