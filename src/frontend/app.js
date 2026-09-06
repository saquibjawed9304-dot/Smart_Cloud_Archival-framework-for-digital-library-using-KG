const API = "http://127.0.0.1:8000";


async function loadStatistics() {

    const response = await fetch(
        `${API}/api/statistics`
    );

    const data = await response.json();

    document.getElementById("bookCount").textContent =
        data.books;

    document.getElementById("authorCount").textContent =
        data.authors;

    document.getElementById("subjectCount").textContent =
        data.subjects;

    document.getElementById("institutionCount").textContent =
        data.institutions;
}


async function searchBooks() {

    const query =
        document.getElementById("searchInput").value;

    const response = await fetch(
        `${API}/api/search?q=${encodeURIComponent(query)}`
    );

    const data = await response.json();

    const results =
        document.getElementById("results");

    document.getElementById("resultCount").textContent =
        `${data.total} results`;

    results.innerHTML = "";

    if (data.results.length === 0) {

        results.innerHTML =
            `<p class="empty">No resources found.</p>`;

        return;
    }

    data.results.forEach(book => {

        const card = document.createElement("div");

        card.className = "result-card";

        card.innerHTML = `
            <h3>${book.title}</h3>

            <div class="metadata">
                <strong>Author:</strong> ${book.author}<br>
                <strong>Subject:</strong> ${book.subject}<br>
                <strong>Institution:</strong> ${book.institution}<br>
                <strong>Language:</strong> ${book.language}<br>
                <strong>Year:</strong> ${book.year ?? "N/A"}
            </div>

            <br>

            <button onclick="loadBookGraph('${book.id}')">
                Explore Connections
            </button>
        `;

        results.appendChild(card);
    });
}


async function loadGraph() {

    const response = await fetch(
        `${API}/api/graph`
    );

    const data = await response.json();

    drawGraph(data);
}


async function loadBookGraph(bookId) {

    const response = await fetch(
        `${API}/api/graph/${bookId}`
    );

    const data = await response.json();

    drawGraph(data);
}


function drawGraph(data) {

    const container =
        document.getElementById("graph");

    container.innerHTML = "";

    if (data.nodes.length === 0) {

        container.innerHTML =
            "<p class='empty'>No graph data.</p>";

        return;
    }

    const width = container.clientWidth || 500;

    const height = 420;

    const centerX = width / 2;
    const centerY = height / 2;

    const nodes = data.nodes;

    nodes.forEach((node, index) => {

        const angle =
            (2 * Math.PI * index) / nodes.length;

        const radius =
            Math.min(width, height) * 0.32;

        const x =
            centerX +
            Math.cos(angle) * radius;

        const y =
            centerY +
            Math.sin(angle) * radius;

        const element =
            document.createElement("div");

        element.className = "graph-node";

        element.textContent =
            `${node.type}: ${node.label}`;

        element.style.left =
            `${x - 70}px`;

        element.style.top =
            `${y - 20}px`;

        container.appendChild(element);
    });
}


async function uploadDocument() {

    const input =
        document.getElementById("fileInput");

    if (!input.files.length) {

        alert("Please select a PDF.");

        return;
    }

    const file = input.files[0];

    const formData = new FormData();

    formData.append("file", file);

    const result =
        document.getElementById("uploadResult");

    result.textContent =
        "Processing document...";

    try {

        const response = await fetch(
            `${API}/api/documents/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        result.textContent =
            JSON.stringify(data, null, 2);

    } catch (error) {

        result.textContent =
            `Upload failed: ${error}`;
    }
}


document
    .getElementById("searchInput")
    .addEventListener("keypress", event => {

        if (event.key === "Enter") {
            searchBooks();
        }

    });


loadStatistics();

loadGraph();