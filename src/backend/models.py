from pydantic import BaseModel
from typing import Optional


class Book(BaseModel):
    id: str
    title: str
    author: str
    subject: str
    institution: str
    language: str
    year: Optional[int] = None


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[Book]