from src.backend.data_store import get_statistics, load_books, search_books


def test_csv_fixture_loads_books():
    books = load_books()
    assert len(books) == 12
    assert books[0]["id"] == "B001"


def test_search_matches_multiple_metadata_fields():
    results = search_books("history")
    assert results
    assert all("history" in str(book).lower() for book in results)


def test_statistics_include_languages():
    statistics = get_statistics()
    assert statistics["books"] == 12
    assert statistics["languages"] == 1