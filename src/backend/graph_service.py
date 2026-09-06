from .data_store import load_books


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

        book_id = f"book:{book['id']}"
        author_id = f"author:{book['author']}"
        subject_id = f"subject:{book['subject']}"
        institution_id = f"institution:{book['institution']}"
        language_id = f"language:{book['language']}"

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

    target = f"book:{book_id}"

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