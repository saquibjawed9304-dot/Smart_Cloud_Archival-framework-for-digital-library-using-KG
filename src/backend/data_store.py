import csv
from typing import Any

from .config import DATASET_FILE, DATA_BACKEND, mysql_connection_config


def _load_csv_books() -> list[dict[str, Any]]:
    if not DATASET_FILE.exists():
        return []

    books = []
    with open(DATASET_FILE, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        required_fields = {"id", "title", "author", "subject", "institution", "language", "year"}
        if not required_fields.issubset(reader.fieldnames or []):
            raise ValueError("The library CSV is missing one or more required columns")

        for row in reader:
            try:
                year = int(row["year"]) if row["year"] else None
            except ValueError:
                year = None
            books.append({
                "id": row["id"].strip(),
                "title": row["title"].strip(),
                "author": row["author"].strip(),
                "subject": row["subject"].strip(),
                "institution": row["institution"].strip(),
                "language": row["language"].strip(),
                "year": year,
            })
    return books


def _mysql_books() -> list[dict[str, Any]]:
    try:
        import mysql.connector
    except ImportError as error:
        raise RuntimeError("mysql-connector-python is required when DATA_BACKEND=mysql") from error

    connection = mysql.connector.connect(**mysql_connection_config())
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, title, author, subject, institution, language, year "
            "FROM books ORDER BY title"
        )
        return list(cursor.fetchall())
    finally:
        connection.close()


def load_books():
    if DATA_BACKEND == "mysql":
        return _mysql_books()
    return _load_csv_books()


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