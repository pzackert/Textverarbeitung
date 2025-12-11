// Review Cockpit Logic - Native Browser Viewer

let currentDocState = {
    projectId: null,
    filename: null,
    originalUrl: null,
    annotatedUrl: null,
    currentView: 'original' // 'original' or 'annotated'
};

// Global function to be called from templates
window.renderDocument = function (filename) {
    const projectId = window.location.pathname.split('/')[2];

    currentDocState.projectId = projectId;
    currentDocState.filename = filename;
    currentDocState.originalUrl = `/projects/${projectId}/files/${filename}`;
    currentDocState.annotatedUrl = `/projects/${projectId}/files/annotated_${filename}`;
    currentDocState.currentView = 'original'; // Reset to original on new doc load

    updateViewer();
    updateToggleUI();
};

// NEW: Open document with citation preferences (Annotated > Original)
window.openDocumentWithCitation = function (preferredFilename, page) {
    console.log(`Open Citation: ${preferredFilename} (Page ${page})`);

    // Check if annotated version exists
    let targetFilename = preferredFilename;

    // Logic: If 'annotiert' is not in name, check if annotated version exists
    if (!targetFilename.includes('annotiert')) {
        const annotatedName = `annotated_${targetFilename}`; // Naming convention
        // Or if the user used suffix:
        const suffixName = targetFilename.replace('.', '_annotiert.');

        if (window.projectFiles && window.projectFiles.includes(suffixName)) {
            targetFilename = suffixName;
        } else if (window.projectFiles && window.projectFiles.includes(annotatedName)) {
            targetFilename = annotatedName;
        }
    }

    window.renderDocument(targetFilename);
};

window.toggleView = function (mode) {
    if (currentDocState.currentView === mode) return;

    // Prevent switching to annotated if not available
    if (mode === 'annotated' && !currentDocState.hasAnnotated) return;

    currentDocState.currentView = mode;
    updateViewer();
    updateToggleUI();
};

// --- Document Rendering Logic ---

async function updateViewer() {
    const viewerFrame = document.getElementById('doc-viewer-frame');
    const viewerContent = document.getElementById('doc-viewer-content');
    const placeholder = document.getElementById('viewer-placeholder');
    const nameLabel = document.getElementById('current-doc-name');
    const downloadLink = document.getElementById('download-link');
    const toggleContainer = document.getElementById('view-toggle-container');

    if (!viewerFrame) return;

    // Reset UI
    viewerFrame.classList.add('hidden');
    viewerContent.classList.add('hidden');
    viewerContent.innerHTML = ''; // Clear previous content
    viewerFrame.src = 'about:blank';
    if (placeholder) placeholder.style.display = 'none';

    // Get URL and extension
    const url = currentDocState.currentView === 'annotated'
        ? currentDocState.annotatedUrl
        : currentDocState.originalUrl;

    const ext = currentDocState.filename.split('.').pop().toLowerCase();

    // Update Header UI
    if (nameLabel) nameLabel.textContent = currentDocState.filename + (currentDocState.currentView === 'annotated' ? ' (Annotiert)' : '');

    if (downloadLink) {
        downloadLink.href = url;
        downloadLink.classList.remove('hidden');
    }

    // Toggle logic for annotated view
    if (toggleContainer) {
        // Check if annotated file exists
        const annotatedName = `annotated_${currentDocState.filename}`;
        const hasAnnotated = window.projectFiles && window.projectFiles.includes(annotatedName);

        // Store in state for UI updates
        currentDocState.hasAnnotated = hasAnnotated;

        // Ensure container is visible (per new requirement)
        toggleContainer.classList.remove('hidden');

        // Reset view if we are in annotated mode but file is gone
        if (currentDocState.currentView === 'annotated' && !hasAnnotated) {
            currentDocState.currentView = 'original';
            // No recursive call, next updateToggleUI will handle visual state
        }
    }

    // --- Rendering Strategy ---
    console.log(`Rendering ${ext} from ${url}`);

    try {
        if (ext === 'pdf') {
            // 1. PDF -> Native Iframe
            viewerFrame.classList.remove('hidden');
            viewerFrame.src = url;

        } else if (['xlsx', 'xls', 'csv'].includes(ext)) {
            // 2. Excel/CSV -> SheetJS
            viewerContent.classList.remove('hidden');
            if (placeholder) placeholder.style.display = 'flex'; // Show loading
            // Add loading indicator manually to content
            viewerContent.innerHTML = '<div class="text-center p-10"><p>Lade Tabellendaten...</p></div>';

            await renderExcel(url, ext, viewerContent);
            if (placeholder) placeholder.style.display = 'none'; // Hide loading

        } else if (['docx'].includes(ext)) {
            // 3. Word -> Mammoth.js
            viewerContent.classList.remove('hidden');
            viewerContent.innerHTML = '<div class="text-center p-10"><p>Lade Dokument...</p></div>';

            await renderWord(url, viewerContent);

        } else if (['txt', 'md', 'json', 'py', 'js', 'html', 'css', 'yaml', 'toml'].includes(ext)) {
            // 4. Text -> Pre Tag
            viewerContent.classList.remove('hidden');
            viewerContent.innerHTML = '<div class="text-center p-10"><p>Lade Text...</p></div>';

            await renderText(url, viewerContent);

        } else if (['pptx', 'ppt'].includes(ext)) {
            // 6. PowerPoint -> Not supported client-side, show download option
            if (placeholder) {
                placeholder.style.display = 'flex';
                placeholder.innerHTML = `
                    <div class="flex flex-col items-center justify-center h-full text-gray-500">
                        <svg class="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8.5v7m0 0l-3-3m3 3l3-3m-9 8v1a3 3 0 003 3h6a3 3 0 003-3v-1"></path>
                        </svg>
                        <p class="text-lg font-medium">PowerPoint-Vorschau nicht verfügbar</p>
                        <p class="text-sm mt-2 text-center max-w-xs">PowerPoint-Dateien erfordern erweiterte Browser-APIs, die noch nicht implementiert sind.</p>
                        <a href="${url}" class="mt-4 text-blue-600 hover:underline font-medium">Datei herunterladen und mit Office öffnen</a>
                    </div>
                `;
            }

        } else {
            // 7. Unsupported -> Show Message
            if (placeholder) {
                placeholder.style.display = 'flex';
                placeholder.innerHTML = `
                    <div class="flex flex-col items-center justify-center h-full text-gray-500">
                        <svg class="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8.5v7m0 0l-3-3m3 3l3-3m-9 8v1a3 3 0 003 3h6a3 3 0 003-3v-1"></path>
                        </svg>
                        <p class="text-lg font-medium">Vorschau nicht verfügbar</p>
                        <p class="text-sm mt-2">Dateityp <code class="bg-gray-200 px-2 py-1 rounded">.${ext}</code> wird nicht unterstützt.</p>
                        <a href="${url}" class="mt-4 text-blue-600 hover:underline font-medium">Datei herunterladen</a>
                    </div>
                `;
            }
        }
    } catch (e) {
        console.error("Rendering failed:", e);
        if (viewerContent) {
            viewerContent.classList.remove('hidden');
            viewerContent.innerHTML = `
                <div class="p-4 bg-red-50 text-red-700 rounded">
                    <strong>Fehler beim Anzeigen:</strong> ${e.message}
                </div>
            `;
        }
    }
}

// --- Specific Render Functions ---

async function renderExcel(url, ext, container) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const arrayBuffer = await response.arrayBuffer();
        if (!arrayBuffer || arrayBuffer.byteLength === 0) {
            throw new Error("Leere Datei");
        }

        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        if (!workbook || !workbook.SheetNames.length) {
            throw new Error("Keine Blätter in der Datei");
        }

        // Render all sheets or just first?
        let html = '';

        if (workbook.SheetNames.length > 1) {
            // Multiple sheets - create tabs
            html += '<div class="mb-4 border-b border-gray-200 flex gap-2">';
            workbook.SheetNames.forEach((name, idx) => {
                html += `<button class="sheet-tab px-3 py-2 text-sm font-medium ${idx === 0 ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600'}" data-sheet-idx="${idx}">${name}</button>`;
            });
            html += '</div>';
        }

        // Render each sheet
        html += '<div class="overflow-x-auto">';
        workbook.SheetNames.forEach((name, idx) => {
            const worksheet = workbook.Sheets[name];
            const tableHtml = XLSX.utils.sheet_to_html(worksheet, {
                id: `excel-table-${idx}`,
                class: 'min-w-full divide-y divide-gray-200'
            });
            html += `<div class="sheet-content ${idx > 0 ? 'hidden' : ''}" data-sheet-idx="${idx}">
                <h3 class="text-sm font-semibold text-gray-700 mb-2 mt-4">${name}</h3>
                <style>
                    #excel-table-${idx} { border-collapse: collapse; width: 100%; }
                    #excel-table-${idx} td, #excel-table-${idx} th { border: 1px solid #e5e7eb; padding: 8px; font-size: 0.875rem; }
                    #excel-table-${idx} tr:first-child td { background-color: #f9fafb; font-weight: 600; }
                </style>
                ${tableHtml}
            </div>`;
        });
        html += '</div>';

        container.innerHTML = html;

        // Add sheet tab functionality
        document.querySelectorAll('.sheet-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const idx = e.target.dataset.sheetIdx;
                document.querySelectorAll('.sheet-tab').forEach(t => {
                    t.className = t.dataset.sheetIdx === idx
                        ? 'sheet-tab px-3 py-2 text-sm font-medium border-b-2 border-blue-500 text-blue-600'
                        : 'sheet-tab px-3 py-2 text-sm font-medium text-gray-600';
                });
                document.querySelectorAll('.sheet-content').forEach(c => {
                    c.classList.toggle('hidden', c.dataset.sheetIdx !== idx);
                });
            });
        });
    } catch (e) {
        throw new Error(`Excel-Datei konnte nicht verarbeitet werden: ${e.message}`);
    }
}

async function renderWord(url, container) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const arrayBuffer = await response.arrayBuffer();
        if (!arrayBuffer || arrayBuffer.byteLength === 0) {
            throw new Error("Leere Datei");
        }

        const result = await mammoth.convertToHtml({ arrayBuffer: arrayBuffer });

        // Add error warnings if any
        let warnings = '';
        if (result.messages && result.messages.length > 0) {
            console.warn('Mammoth warnings:', result.messages);
        }

        container.innerHTML = `
            <div class="prose prose-sm max-w-none p-8 bg-white min-h-full">
                <style>
                    .prose h1 { @apply text-2xl font-bold mt-6 mb-3; }
                    .prose h2 { @apply text-xl font-bold mt-5 mb-2; }
                    .prose h3 { @apply text-lg font-bold mt-4 mb-2; }
                    .prose p { @apply mb-3; }
                    .prose ul, .prose ol { @apply mb-3 ml-4; }
                    .prose li { @apply mb-1; }
                    .prose strong { @apply font-bold; }
                    .prose em { @apply italic; }
                    .prose u { @apply underline; }
                    .prose table { @apply border-collapse border border-gray-300; }
                    .prose td, .prose th { @apply border border-gray-300 p-2; }
                </style>
                ${result.value}
            </div>
            ${warnings}
        `;
    } catch (e) {
        throw new Error(`Word-Datei konnte nicht verarbeitet werden: ${e.message}`);
    }
}

async function renderText(url, container) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const text = await response.text();
        if (text === null || text === undefined) {
            throw new Error("Leere Datei");
        }

        // Escape HTML for safety
        const escaped = text.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        const lineCount = text.split('\n').length;

        container.innerHTML = `
            <div class="flex flex-col h-full">
                <div class="text-xs text-gray-500 px-4 py-2 border-b border-gray-200">
                    ${lineCount} Zeilen
                </div>
                <pre class="flex-1 whitespace-pre-wrap font-mono text-xs bg-gray-50 p-4 overflow-auto border-l-4 border-gray-300" style="tab-size: 4;">${escaped}</pre>
            </div>
        `;
    } catch (e) {
        throw new Error(`Text konnte nicht geladen werden: ${e.message}`);
    }
}

function updateToggleUI() {
    const container = document.getElementById('view-toggle-container');
    const btnOriginal = document.getElementById('btn-original');
    const btnAnnotated = document.getElementById('btn-annotated');

    if (!container || !btnOriginal || !btnAnnotated) return;

    // Show toggle container (it's always visible now per logic in updateViewer)
    container.classList.remove('hidden');

    const hasAnnotated = currentDocState.hasAnnotated;

    // Button Styles
    // Original: Always enabled
    if (currentDocState.currentView === 'original') {
        btnOriginal.className = "px-3 py-1 text-xs font-medium rounded-md bg-white shadow-sm text-gray-800 transition-all";

        if (hasAnnotated) {
            btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded-md text-gray-500 hover:text-gray-700 transition-all cursor-pointer";
            btnAnnotated.disabled = false;
        } else {
            // Disabled state
            btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded-md text-gray-300 cursor-not-allowed bg-gray-50 pointer-events-none select-none";
            btnAnnotated.disabled = true;
        }
    } else {
        // Annotated View Active (implies hasAnnotated is true)
        btnOriginal.className = "px-3 py-1 text-xs font-medium rounded-md text-gray-500 hover:text-gray-700 transition-all cursor-pointer";
        btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded-md bg-white shadow-sm text-gray-800 transition-all";
        btnAnnotated.disabled = false;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Review Cockpit initialized (Native Viewer + Toggle)');
});
