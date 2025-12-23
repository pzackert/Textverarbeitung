class DocumentViewer {
    constructor() {
        // Renderers map
        this.renderers = {
            pdf: new PdfRenderer('pdf-viewer-container'),
            docx: new DocxRenderer('doc-viewer-content'),
            xlsx: new XlsxRenderer('doc-viewer-content'),
            txt: new TextRenderer('doc-viewer-content')
        };

        this.activeRenderer = null;
        this.placeholder = document.getElementById('viewer-placeholder');
    }

    async stop() {
        if (this.activeRenderer) {
            await this.activeRenderer.destroy();
            this.activeRenderer = null;
        }
        if (this.placeholder) this.placeholder.style.display = 'flex';
    }

    async loadDocument(filename, format, originalUrl, annotatedUrl, hasAnnotated, initialView = 'original') {
        await this.stop();
        if (this.placeholder) this.placeholder.style.display = 'none';

        // Update State
        ReviewState.currentDocument = { filename, format, originalUrl, annotatedUrl, hasAnnotated };
        ReviewState.currentView = (initialView === 'annotated' && hasAnnotated) ? 'annotated' : 'original';

        // Select Renderer
        const ext = format || filename.split('.').pop().toLowerCase();

        let renderer = null;
        if (ext === 'pdf') renderer = this.renderers.pdf;
        else if (ext === 'docx') renderer = this.renderers.docx;
        else if (['xlsx', 'xls', 'csv'].includes(ext)) renderer = this.renderers.xlsx;
        else renderer = this.renderers.txt; // Fallback text

        this.activeRenderer = renderer;

        // URL to load
        const urlToCheck = (ReviewState.currentView === 'annotated' && hasAnnotated) ? annotatedUrl : originalUrl;

        console.log(`Viewer loading: ${filename} (${ext}) -> ${urlToCheck}`);

        await renderer.load(urlToCheck);

        // Update Header UI
        this.updateHeaderUI();
    }

    async toggleView(mode) {
        if (mode === ReviewState.currentView) return;
        if (mode === 'annotated' && !ReviewState.currentDocument.hasAnnotated) return;

        ReviewState.currentView = mode;
        const url = (mode === 'annotated') ? ReviewState.currentDocument.annotatedUrl : ReviewState.currentDocument.originalUrl;

        if (this.activeRenderer) {
            // Re-load with new URL
            // Should we destroy active renderer? For PDF maybe just load(url)?
            // PdfRenderer.load() handles cancel internally.
            await this.activeRenderer.load(url, ReviewState.currentPage);
        }
        this.updateHeaderUI();
    }

    updateHeaderUI() {
        document.getElementById('current-doc-name').textContent = ReviewState.currentDocument.filename + (ReviewState.currentView === 'annotated' ? ' (Annotiert)' : '');

        const btnOriginal = document.getElementById('btn-original');
        const btnAnnotated = document.getElementById('btn-annotated');

        if (btnOriginal) {
            btnOriginal.className = ReviewState.currentView === 'original'
                ? "px-3 py-1 text-xs font-semibold rounded bg-white shadow text-gray-900 border"
                : "px-3 py-1 text-xs font-medium rounded text-gray-500 hover:text-gray-900";
        }

        if (btnAnnotated) {
            btnAnnotated.disabled = !ReviewState.currentDocument.hasAnnotated;
            if (ReviewState.currentDocument.hasAnnotated) {
                btnAnnotated.className = ReviewState.currentView === 'annotated'
                    ? "px-3 py-1 text-xs font-semibold rounded bg-white shadow text-gray-900 border"
                    : "px-3 py-1 text-xs font-medium rounded text-gray-500 hover:text-gray-900";
            } else {
                btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded text-gray-300 cursor-not-allowed";
            }
        }
    }
}

window.DocumentViewer = DocumentViewer;
