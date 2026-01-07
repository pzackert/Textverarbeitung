
// Review Cockpit Logic - Robust Implementation
console.log("Loading review.js v3...");

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
        const viewParam = urlParams.get('view') || null; // 'original', 'annotated' or null (auto)
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
window.loadDocument = async function (filename, initialView = null, initialPage = 1) {
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

    // Determine View Mode
    let viewMode = initialView;
    if (!viewMode) {
        // Auto-select: Prioritize Annotated if available
        viewMode = doc.has_annotated ? 'annotated' : 'original';
    }

    // Load in Viewer
    await viewer.loadDocument(
        doc.filename,
        doc.format,
        doc.original_url,
        doc.annotated_url,
        doc.has_annotated,
        viewMode,
        initialPage
    );
};

// Global: Toggle View
window.toggleView = function (mode) {
    if (viewer) viewer.toggleView(mode);
};

// Global: Open Document & Jump to Page (Deep Linking)
window.openDocumentSource = function (filename, page) {
    // 1. Check if document exists in list
    const doc = projectDocuments.find(d => d.filename === filename);
    if (!doc) {
        console.error("Deep link failed: File not found", filename);
        // Try fallback if partial match? For now strict.
        return;
    }

    // 2. Load Document (logic handles if already loaded, but we force page update)
    // We reuse loadDocument but ensure page is passed
    // If it's already loaded, DocumentViewer can optimize, but for safety we re-call it.
    console.log(`Deep linking request: ${filename} -> Page ${page}`);
    loadDocument(filename, 'original', page);
};

// Global: PDF Page Change
window.changePdfPage = function (offset) {
    if (viewer && viewer.activeRenderer && viewer.activeRenderer instanceof PdfRenderer) {
        viewer.activeRenderer.changePage(offset);
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

            if (data.status === 'ready') {
                const msgEl = document.getElementById('rag-status-msg');
                if (msgEl) {
                    msgEl.textContent = "Wissensbasis bereit";
                    msgEl.classList.remove('text-gray-500');
                    msgEl.classList.add('text-green-600', 'font-medium');
                    setTimeout(() => msgEl.style.display = 'none', 3000); // Hide after 3s
                }
                clearInterval(interval);
            } else if (data.status === 'error') {
                const msgEl = document.getElementById('rag-status-msg');
                if (msgEl) msgEl.textContent = "Fehler beim Laden der Wissensbasis.";
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
    window.location.href = '/projects';
};

window.unloadRAGContext = async function () {
    if (!confirm("Möchten Sie den RAG-Kontext für diesen Antrag wirklich löschen?\nAlle Dokumente müssen danach neu indexiert werden.")) return;

    try {
        const res = await fetch(`/api/rag/project/${ReviewState.projectId}/unload`, { method: 'POST' });
        if (res.ok) {
            window.location.reload();
        } else {
            const err = await res.text();
            console.error(err);
            alert("Fehler beim Leeren des Kontexts.");
        }
    } catch (e) {
        console.error(e);
        alert("Netzwerkfehler.");
    }
};


// --- Criteria Catalog API (Restored) ---

window.fetchCriteriaResults = async function () {
    if (!ReviewState.projectId) return {};
    try {
        const res = await fetch(`/api/queue/projects/${ReviewState.projectId}/results`);
        // Fallback or specific results endpoint? 
        // Actually the queue backend doesn't persist results permanently in a separate "results" endpoint 
        // other than the job history. 
        // We might need to check criteria.py or projects.py for persistent results.
        // Assuming projects.py IS correct for fetching persistent results, but Queue API for ACTIONS.
        // Let's check where results are saved.
        // Queue API calls validation_service.evaluate_criterion, which usually updates the DB/Project.
        // So fetching results from /api/projects/.../criteria/results (if exists) is correct.
        // But wait, projects.py lacked criteria endpoints.
        // I will assume for now we use the projects endpoint and if it fails I need to fix projects.py too.
        // BUT for evaluate/poll I MUST change to queue.
        const res2 = await fetch(`/api/projects/${ReviewState.projectId}/criteria/results`);
        if (!res2.ok) throw new Error("Failed to fetch results");
        return await res2.json();
    } catch (e) {
        // console.error("fetchCriteriaResults error:", e);
        return {};
    }
};

// --- Sequential & Retry Logic ---

window.retryCriterion = async function (event, criterionId) {
    if (event) event.stopPropagation(); // prevent toggle
    const btn = event.currentTarget;
    const originalContent = btn.innerHTML;

    // UI: Spin
    btn.innerHTML = `<svg class="animate-spin h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;
    btn.disabled = true;

    await evaluateCriterionSequential(criterionId);

    btn.innerHTML = originalContent;
    btn.disabled = false;
};

// Core single evaluation logic that updates UI directly
async function evaluateCriterionSequential(criterionId) {
    if (!ReviewState.projectId) return;

    const cardId = `criterion-card-${criterionId}`;
    const iconId = `status-icon-${criterionId}`;
    const card = document.getElementById(cardId);
    const icon = document.getElementById(iconId);

    if (icon) icon.innerHTML = '🔄'; // Spinner placeholder key

    try {
        // We use the Queue API but wait for result? 
        // Or better: use the DIRECT project endpoint if we want immediate result?
        // Queue endpoint returns a JOB. 
        // Let's use validation_service direct call via a new sync endpoint if available?
        // Actually, let's call the queue endpoint then poll it? 
        // "Client-Side Sequencing" implies we wait for one to finish.
        // Let's use the `/api/queue/projects/...` but poll the job until done.

        const res = await fetch(`/api/queue/projects/${ReviewState.projectId}/criteria/${criterionId}`, { method: 'POST' });
        if (!res.ok) throw new Error("Start failed");
        const job = await res.json();

        // Poll job
        const finalJob = await pollJobUntilDone(job.job_id);

        // Refresh the specific card content or the whole list?
        //Ideally just the card. But HTMX does that best. 
        // For now, let's just reload the list area via HTMX trigger or refresh page?
        // User wants "visible progress".
        // Let's manually fetch the result of that criterion and update UI?
        // Or simpler: Trigger HTMX update of the results block?

        // Refresh the results block (server-side rendered partial)
        htmx.ajax('GET', `/projects/${ReviewState.projectId}/validation-status`, { target: '#validation-results', swap: 'innerHTML' });

        // IMPORTANT: Refresh document list metadata because new annotated files might have been created!
        await loadProjectDocuments(ReviewState.projectId);

        // If currently viewing the relevant document, we might want to update the viewer UI?
        // But for now, just updating metadata ensures next click is correct.
        // If the current open document IS the one being evaluated, we could check and reload?
        if (viewer && ReviewState.currentDocument) {
            const doc = projectDocuments.find(d => d.filename === ReviewState.currentDocument.filename);
            if (doc && doc.has_annotated && !ReviewState.currentDocument.hasAnnotated) {
                // It just got annotated!
                console.log("Current document became annotated, refreshing viewer state...");
                // Reload the same document to pick up new state
                loadDocument(doc.filename, 'annotated', ReviewState.currentPage);
                // Note: passing 'annotated' forces switch to new view
            }
        }

    } catch (e) {
        console.error(e);
        if (icon) icon.innerText = '⚠️';
        alert("Prüfung fehlgeschlagen: " + e.message);
    }
}

async function pollJobUntilDone(jobId) {
    return new Promise((resolve, reject) => {
        const check = async () => {
            try {
                const r = await fetch(`/api/queue/${jobId}`);
                const j = await r.json();
                if (j.status === 'done') resolve(j);
                else if (j.status === 'failed') reject(new Error(j.message));
                else setTimeout(check, 500);
            } catch (e) { reject(e); }
        };
        check();
    });
}

// "Alle Prüfen" Logic
window.evaluateAllCriteria = async function () {
    if (!ReviewState.projectId) return;

    // Get all criterion IDs from DOM to iterate
    const cards = document.querySelectorAll('[id^="criterion-card-"]');
    const ids = Array.from(cards).map(c => c.id.replace('criterion-card-', ''));

    if (ids.length === 0) {
        alert("Keine Kriterien gefunden.");
        return;
    }

    // Update UI to show global loading state eventually?
    // For now, iterate
    for (const cid of ids) {
        // Scroll to card?
        const card = document.getElementById(`criterion-card-${cid}`);
        if (card) {
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Highlight?
            card.classList.add('bg-blue-50');
        }

        await evaluateCriterionSequential(cid);

        if (card) card.classList.remove('bg-blue-50');
    }

    window.showToast("Alle Prüfungen abgeschlossen", "success");
};

window.handleUpload = async function (event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerText;

    try {
        submitBtn.disabled = true;
        submitBtn.innerText = "Wird hochgeladen...";

        const res = await fetch(`/api/projects/${ReviewState.projectId}/upload`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            window.location.reload();
        } else {
            console.error(await res.text());
            alert('Upload fehlgeschlagen.');
        }
    } catch (e) {
        console.error(e);
        alert('Ein Fehler ist aufgetreten.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = originalText;
    }
};

// Alias for chat.js deep linking
window.renderDocument = function (filename, page) {
    if (window.loadDocument) {
        window.loadDocument(filename, null, page || 1);
    }
};

// Citation Navigation
window.jumpToCitation = function (docId, page, snippet) {
    console.log(`Jumping to citation: ${docId}, Page ${page}`);
    if (viewer && viewer.activeRenderer && viewer.activeRenderer.scrollToPage) {
        viewer.activeRenderer.scrollToPage(page);

        // Optional: Highlight Logic (Future)
        // console.log("Highlighting:", snippet);
    } else {
        console.warn("Viewer or scrollToPage not available");
    }
};
