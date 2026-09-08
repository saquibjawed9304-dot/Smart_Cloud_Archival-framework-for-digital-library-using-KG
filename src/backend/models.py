from pydantic import BaseModel, Field
from typing import Any, Optional


class Book(BaseModel):
    id: str
    title: str
    author: str
    subject: str
    institution: str
    language: str
    year: Optional[int] = None
    pdf_status: str = "available"
    read_url: Optional[str] = None
    download_url: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[Book]


class Statistics(BaseModel):
    books: int
    authors: int
    subjects: int
    institutions: int
    languages: int


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    label: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class DocumentResult(BaseModel):
    status: str
    filename: str
    document_id: Optional[str] = None
    characters_extracted: int = 0
    text_preview: str = ""
    read_url: Optional[str] = None
    download_url: Optional[str] = None
    entities: list[dict[str, Any]] = Field(default_factory=list)
    relationships: list[dict[str, Any]] = Field(default_factory=list)


class DocumentSummary(BaseModel):
    id: str
    filename: str
    size_bytes: int
    characters_extracted: int = 0
    status: str = "stored"
    read_url: Optional[str] = None
    download_url: Optional[str] = None