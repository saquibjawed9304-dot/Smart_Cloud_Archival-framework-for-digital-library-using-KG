const API = window.ARCHIVAL_API || (
    window.location.port === "5500"
        ? "http://127.0.0.1:8000"
        : ""
);

const byId = id => document.getElementById(id);
let activeTab = "books";
let searchTimer;
let lastGraphData;

async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
    }
    return data;
}

function setMessage(element, message, type = "") {
    element.textContent = message;
    element.className = `status-message ${type}`.trim();
}


function addLinkButton(card, label, url, download = false) {
    const link = document.createElement("a");
    link.className = "action-button";
    link.href = `${API}${url}`;
    link.textContent = label;
    if (download) link.setAttribute("download", "");
    card.appendChild(link);
}


function addReadButton(card, label, url, title) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "action-button";
    button.textContent = label;
    button.addEventListener("click", () => openPdfViewer(url, title));
    card.appendChild(button);
}


function addDeleteButton(card, documentId, filename) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "action-button danger-button";
    button.textContent = "Remove PDF";
    button.addEventListener("click", async () => {
        if (!window.confirm(`Remove ${filename} from the archive?`)) return;
        button.disabled = true;
        try {
            await request(`/api/documents/${encodeURIComponent(documentId)}`, { method: "DELETE" });
            await showDocuments();
        } catch (error) {
            button.disabled = false;
            setMessage(byId("results"), `Could not remove PDF: ${error.message}`, "error");
        }
    });
    card.appendChild(button);
}


function openPdfViewer(url, title) {
    byId("pdfViewerTitle").textContent = `Reading: ${title}`;
    byId("pdfViewer").src = `${API}${url}`;
    byId("pdfViewerSection").hidden = false;
    byId("pdfViewerSection").scrollIntoView({ behavior: "smooth", block: "start" });
}


function closePdfViewer() {
    byId("pdfViewer").src = "about:blank";
    byId("pdfViewerSection").hidden = true;
}


async function loadStatistics() {

    const data = await request("/api/statistics");

    document.getElementById("bookCount").textContent =
        data.books;

    document.getElementById("authorCount").textContent =
        data.authors;

    document.getElementById("subjectCount").textContent =
        data.subjects;

    byId("institutionCount").textContent = data.institutions;
    byId("languageCount").textContent = data.languages;
}


async function searchBooks() {

    const query =
        document.getElementById("searchInput").value;

    const results = byId("results");
    setMessage(results, "Searching the collection...", "loading");

    const data = await request(`/api/search?q=${encodeURIComponent(query)}`);

    if (activeTab === "documents") {
        const documents = await request("/api/documents");
        const normalizedQuery = query.trim().toLowerCase();
        const filteredDocuments = normalizedQuery
            ? documents.filter(document => document.filename.toLowerCase().includes(normalizedQuery))
            : documents;
        renderDocuments(filteredDocuments);
        byId("resultCount").textContent = `${filteredDocuments.length} PDFs`;
        return;
    }

    byId("resultCount").textContent =
        `${data.total} results`;

    results.replaceChildren();

    if (data.results.length === 0) {

        const empty = document.createElement("p");
        empty.className = "empty";
        empty.textContent = "No resources found.";
        results.appendChild(empty);

        return;
    }

    data.results.forEach(book => {

        const card = document.createElement("div");

        card.className = "result-card";

        const title = document.createElement("h3");
        title.textContent = book.title;
        const metadata = document.createElement("div");
        metadata.className = "metadata";
        metadata.textContent = `By ${book.author} | ${book.subject} | ${book.institution} | ${book.language} | ${book.year ?? "Year unavailable"}`;
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = "Explore connections";
        button.addEventListener("click", () => loadBookGraph(book.id));
        const pdfState = document.createElement("span");
        pdfState.className = "file-state";
        pdfState.textContent = "Blank PDF placeholder available";
        const actions = document.createElement("div");
        actions.className = "card-actions";
        actions.appendChild(button);
        card.append(title, metadata, pdfState, actions);
        addReadButton(actions, "Read book", book.read_url, book.title);
        addLinkButton(actions, "Download PDF", book.download_url, true);

        results.appendChild(card);
    });
}


function renderDocuments(documents) {
    const results = byId("results");
    results.replaceChildren();
    if (documents.length === 0) {
        const empty = document.createElement("p");
        empty.className = "empty";
        empty.textContent = "No uploaded PDFs yet.";
        results.appendChild(empty);
        return;
    }
    documents.forEach(uploadedDocument => {
        const card = document.createElement("div");
        card.className = "result-card document-card";
        const title = document.createElement("h3");
        title.textContent = uploadedDocument.filename;
        const metadata = document.createElement("div");
        metadata.className = "metadata";
        metadata.textContent = `${formatBytes(uploadedDocument.size_bytes)} | ${uploadedDocument.status}`;
        const state = document.createElement("span");
        state.className = "file-state attached";
        state.textContent = "PDF stored in archive";
        const actions = document.createElement("div");
        actions.className = "card-actions";
        card.append(title, metadata, state, actions);
        addReadButton(actions, "Read PDF", uploadedDocument.read_url, uploadedDocument.filename);
        addLinkButton(actions, "Download PDF", uploadedDocument.download_url, true);
        addDeleteButton(actions, uploadedDocument.id, uploadedDocument.filename);
        results.appendChild(card);
    });
}


function formatBytes(bytes) {
    if (!bytes) return "Empty PDF";
    if (bytes < 1024) return `${bytes} bytes`;
    return `${(bytes / 1024).toFixed(1)} KB`;
}


async function showBooks() {
    activeTab = "books";
    byId("booksTab").classList.add("active");
    byId("documentsTab").classList.remove("active");
    await searchBooks();
}


async function showDocuments() {
    activeTab = "documents";
    byId("documentsTab").classList.add("active");
    byId("booksTab").classList.remove("active");
    await searchBooks();
}


async function loadGraph() {

    try {
        drawGraph(await request("/api/graph"));
    } catch (error) {
        showGraphError(error.message);
    }
}


async function loadBookGraph(bookId) {

    try {
        drawGraph(await request(`/api/graph/${encodeURIComponent(bookId)}`));
    } catch (error) {
        showGraphError(error.message);
    }
}

function showGraphError(message) {
    const graph = byId("graph");
    graph.replaceChildren();
    setMessage(graph, message, "error");
}


function drawGraph(data) {

    const container = document.getElementById("graph");

    container.replaceChildren();

    if (data.nodes.length === 0) {
        setMessage(container, "No graph data.");
        return;
    }

    const width = container.clientWidth || 600;
    lastGraphData = data;
    const height = Math.max(430, Math.min(560, container.clientHeight || 500));

    /*
     * Create SVG layer for relationships.
     */
    const svg = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "svg"
    );

    svg.setAttribute("width", "100%");
    svg.setAttribute("height", height);
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

    svg.style.position = "absolute";
    svg.style.left = "0";
    svg.style.top = "0";

    container.appendChild(svg);


    /*
     * Position nodes in a circle.
     */
    const positions = {};

    data.nodes.forEach((node, index) => {

        const angle =
            (2 * Math.PI * index) / data.nodes.length;

        const radius =
            Math.min(width, height) * 0.34;

        const x =
            width / 2 +
            Math.cos(angle) * radius;

        const y =
            height / 2 +
            Math.sin(angle) * radius;

        positions[node.id] = {
            x: x,
            y: y
        };
    });


    /*
     * Draw relationships.
     */
    data.edges.forEach(edge => {

        const source = positions[edge.source];
        const target = positions[edge.target];

        if (!source || !target) {
            return;
        }

        const line = document.createElementNS(
            "http://www.w3.org/2000/svg",
            "line"
        );

        line.setAttribute("x1", source.x);
        line.setAttribute("y1", source.y);

        line.setAttribute("x2", target.x);
        line.setAttribute("y2", target.y);

        line.setAttribute(
            "stroke",
            "#94a3b8"
        );

        line.setAttribute(
            "stroke-width",
            "2"
        );

        svg.appendChild(line);
    });


    /*
     * Draw nodes.
     */
    data.nodes.forEach(node => {

        const position = positions[node.id];

            const element = document.createElement("div");

        element.className = "graph-node";

        element.textContent =
            `${node.type}: ${node.label}`;

        element.style.left =
            `${position.x - 70}px`;

        element.style.top =
            `${position.y - 22}px`;

        container.appendChild(element);
    });
}


async function uploadDocument() {

    const input = byId("fileInput");

    if (!input.files.length) {

        setMessage(byId("uploadResult"), "Please select a PDF.", "error");

        return;
    }

    const file = input.files[0];

    const formData = new FormData();

    formData.append("file", file);

    const result = byId("uploadResult");

    result.textContent =
        "Processing document...";

    try {

        const data = await request("/api/documents/upload", { method: "POST", body: formData });
        setMessage(result, `${data.filename} processed: ${data.characters_extracted} characters extracted.`, "success");
        await showDocuments();

    } catch (error) {

        setMessage(result, `Upload failed: ${error.message}`, "error");
    }
}


byId("searchInput")
    .addEventListener("keydown", event => {

        if (event.key === "Enter") {
            event.preventDefault();
            searchBooks().catch(error => setMessage(byId("results"), error.message, "error"));
        }

    });

byId("searchInput").addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => searchBooks().catch(error => setMessage(byId("results"), error.message, "error")), 250);
});
byId("searchButton").addEventListener("click", () => searchBooks().catch(error => setMessage(byId("results"), error.message, "error")));
byId("booksTab").addEventListener("click", () => showBooks().catch(error => setMessage(byId("results"), error.message, "error")));
byId("documentsTab").addEventListener("click", () => showDocuments().catch(error => setMessage(byId("results"), error.message, "error")));
byId("refreshGraph").addEventListener("click", loadGraph);
byId("uploadButton").addEventListener("click", uploadDocument);
byId("closePdfViewer").addEventListener("click", closePdfViewer);
window.addEventListener("resize", () => {
    if (lastGraphData) drawGraph(lastGraphData);
});


Promise.all([
    loadStatistics().catch(error => setMessage(byId("results"), error.message, "error")),
    searchBooks().catch(error => setMessage(byId("results"), error.message, "error")),
    loadGraph(),
]);