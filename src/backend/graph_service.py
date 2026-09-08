from .data_store import load_books
from fastapi import HTTPException


def _node_id(node_type: str, label: str) -> str:
    normalized = "-".join(label.casefold().split())
    return f"{node_type.casefold()}:{normalized}"


def build_graph():
    books = load_books()

    nodes = []
    edges = []

    added_nodes = set()

    def add_node(node_id, label, node_type):
        if node_id not in added_nodes:
            nodes.append({
                "id": node_id,
                "label": label,
                "type": node_type
            })
            added_nodes.add(node_id)

    for book in books:

        book_id = _node_id("book", book["id"])
        author_id = _node_id("author", book["author"])
        subject_id = _node_id("subject", book["subject"])
        institution_id = _node_id("institution", book["institution"])
        language_id = _node_id("language", book["language"])

        add_node(book_id, book["title"], "Book")
        add_node(author_id, book["author"], "Author")
        add_node(subject_id, book["subject"], "Subject")
        add_node(institution_id, book["institution"], "Institution")
        add_node(language_id, book["language"], "Language")

        edges.append({
            "source": book_id,
            "target": author_id,
            "label": "WRITTEN_BY"
        })

        edges.append({
            "source": book_id,
            "target": subject_id,
            "label": "ABOUT"
        })

        edges.append({
            "source": book_id,
            "target": institution_id,
            "label": "PUBLISHED_BY"
        })

        edges.append({
            "source": book_id,
            "target": language_id,
            "label": "IN_LANGUAGE"
        })

    return {
        "nodes": nodes,
        "edges": edges
    }


def get_book_graph(book_id: str):
    graph = build_graph()

    target = _node_id("book", book_id)

    if target not in {node["id"] for node in graph["nodes"]}:
        raise HTTPException(status_code=404, detail=f"Book '{book_id}' was not found")

    connected_ids = {target}

    for edge in graph["edges"]:
        if edge["source"] == target:
            connected_ids.add(edge["target"])

    nodes = [
        node
        for node in graph["nodes"]
        if node["id"] in connected_ids
    ]

    edges = [
        edge
        for edge in graph["edges"]
        if edge["source"] in connected_ids
        and edge["target"] in connected_ids
    ]

    return {
        "nodes": nodes,
        "edges": edges
    }