
// Review Cockpit Logic - Robust Implementation
console.log("Loading review.js...");

// Configure PDF.js Worker (Essential!)
if (typeof pdfjsLib !== 'undefined') {
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/js/libs/pdf.worker.min.js';
    console.log("PDF.js worker configured.");
} else {
    console.error("Critical: pdfjsLib is undefined. PDF rendering will fail.");
}

// Global Viewer Instance
let viewer = null;
let projectDocuments = []; // Local cache of document metadata

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Review Cockpit DOMContentLoaded');

    try {
        // Init Viewer
        if (typeof DocumentViewer === 'undefined') {
            throw new Error("DocumentViewer class is missing!");
        }
        viewer = new DocumentViewer();
        console.log("Viewer initialized.");
    } catch (e) {
        console.error("Viewer initialization failed:", e);
        return;
    }

    // Get Project ID from URL
    const pathParts = window.location.pathname.split('/');
    if (pathParts[1] === 'projects' && pathParts[2]) {
        ReviewState.projectId = pathParts[2];

        // Load Document List Metadata
        await loadProjectDocuments(ReviewState.projectId);

        // Auto-Open Logic (Deep Linking or First)
        const urlParams = new URLSearchParams(window.location.search);
        const docParam = urlParams.get('doc');
        const viewParam = urlParams.get('view') || 'original'; // 'original' or 'annotated'
        const pageParam = parseInt(urlParams.get('page')) || 1;

        if (docParam) {
            console.log(`Deep linking to ${docParam} page ${pageParam}`);
            const target = projectDocuments.find(d => d.filename === docParam);
            if (target) {
                loadDocument(docParam, viewParam, pageParam);
            } else {
                console.warn("Deep linked doc not found in list, fallback to first.");
                if (projectDocuments.length > 0) loadDocument(projectDocuments[0].filename);
            }
        } else {
            // Default: First doc
            if (projectDocuments.length > 0) {
                const firstDoc = projectDocuments[0];
                loadDocument(firstDoc.filename);
            }
        }

        // Start RAG Ingestion (Background)
        loadProjectRAG(ReviewState.projectId);
    }
});

async function loadProjectDocuments(projectId) {
    try {
        const res = await fetch(`/api/projects/${projectId}/documents`);
        const data = await res.json();
        projectDocuments = data.documents;
        console.log("Loaded documents metadata:", projectDocuments);
    } catch (e) {
        console.error("Failed to load document list", e);
    }
}

// Global: Load Document by Filename (Called from Sidebar or Deep Link)
window.loadDocument = async function (filename, initialView = 'original', initialPage = 1) {
    if (!viewer) return;

    // Find metadata
    const doc = projectDocuments.find(d => d.filename === filename);
    if (!doc) {
        console.error("Document metadata not found for:", filename);
        // Fallback or retry fetch?
        return;
    }

    // Highlight Sidebar
    document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
    const btn = document.querySelector(`button[data-filename="${filename}"]`);
    if (btn) btn.classList.add('active');

    // Load in Viewer
    await viewer.loadDocument(
        doc.filename,
        doc.format,
        doc.original_url,
        doc.annotated_url,
        doc.has_annotated,
        initialView,
        initialPage
    );
};

// Global: Toggle View
window.toggleView = function (mode) {
    if (viewer) viewer.toggleView(mode);
};

// Global: PDF Page Change
window.changePdfPage = function (offset) {
    if (viewer && viewer.activeRenderer && viewer.activeRenderer instanceof PdfRenderer) {
        if (offset === 1) viewer.activeRenderer.onNextPage();
        else viewer.activeRenderer.onPrevPage();
    }
};

// --- RAG & Status Logic (Preserved) ---

async function loadProjectRAG(projectId) {
    const statusEl = document.getElementById('rag-status-msg');
    try {
        // Simple check or auto-ingest
        const res = await fetch(`/api/rag/project/${projectId}/ingest`, { method: 'POST' });
        if (res.ok) {
            pollIngestionStatus(projectId);
        }
    } catch (e) { console.error(e); }
}

async function pollIngestionStatus(projectId) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/api/rag/project/${projectId}/status`);
            const data = await res.json();

            // Update sidebar icons based on status
            if (data.files) {
                for (const [filename, fileState] of Object.entries(data.files)) {
                    updateFileIcon(filename, fileState.status);
                }
            }

            if (data.status === 'ready' || data.status === 'error') {
                clearInterval(interval);
            }
        } catch (e) { clearInterval(interval); }
    }, 2000);
}

function updateFileIcon(filename, status) {
    const safeName = filename.replace(/\./g, '_');
    const wrapper = document.getElementById(`doc-wrapper-${safeName}`);
    if (!wrapper) return;

    // Helper to toggle opacity
    const setOpacity = (sel, opacity) => {
        const el = wrapper.querySelector(sel);
        if (el) el.classList.toggle('opacity-0', opacity === 0);
        if (el) el.classList.toggle('opacity-100', opacity === 1);
    }

    // Reset
    setOpacity('.status-icon-static', 0);
    setOpacity('.status-icon-loading', 0);
    setOpacity('.status-icon-success', 0);
    setOpacity('.status-icon-error', 0);

    if (status === 'loading') setOpacity('.status-icon-loading', 1);
    else if (status === 'ready') setOpacity('.status-icon-success', 1);
    else if (status === 'error') setOpacity('.status-icon-error', 1);
    else setOpacity('.status-icon-static', 1);
}

window.cleanupAndExit = async function (event) {
    // Optional: Call unload API
    window.location.href = '/projects';
};

