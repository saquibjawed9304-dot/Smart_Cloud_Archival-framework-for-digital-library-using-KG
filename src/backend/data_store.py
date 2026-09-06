import csv
from pathlib import Path

from .config import DATASET_FILE


def load_books():
    if not DATASET_FILE.exists():
        return []

    books = []

    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            books.append({
                "id": row["id"],
                "title": row["title"],
                "author": row["author"],
                "subject": row["subject"],
                "institution": row["institution"],
                "language": row["language"],
                "year": int(row["year"]) if row["year"] else None
            })

    return books


def search_books(query: str):
    books = load_books()

    if not query:
        return books

    query = query.lower().strip()

    results = []

    for book in books:
        searchable = " ".join([
            book["title"],
            book["author"],
            book["subject"],
            book["institution"],
            book["language"]
        ]).lower()

        if query in searchable:
            results.append(book)

    return results


def get_statistics():
    books = load_books()

    authors = set(book["author"] for book in books)
    subjects = set(book["subject"] for book in books)
    institutions = set(book["institution"] for book in books)
    languages = set(book["language"] for book in books)

    return {
        "books": len(books),
        "authors": len(authors),
        "subjects": len(subjects),
        "institutions": len(institutions),
        "languages": len(languages)
    }