class PdfRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scrollContainer = document.getElementById('pdf-scroll-container');
        this.canvas = document.createElement('canvas');
        this.canvas.className = 'shadow-2xl';
        if (this.scrollContainer) {
            this.scrollContainer.innerHTML = ''; // Clear previous if any
            this.scrollContainer.appendChild(this.canvas);
        } else {
            // Fallback if scroll container missing in template
            this.container.appendChild(this.canvas);
        }
        this.ctx = this.canvas.getContext('2d');

        this.pdfDoc = null;
        this.pageNum = 1;
        this.pageRendering = false;
        this.pageNumPending = null;
        this.scale = 1.5;
        this.renderTask = null;
    }

    async load(url, initialPage = 1) {
        this.show();
        try {
            // Cancel previous render if any
            if (this.renderTask) {
                await this.renderTask.cancel();
            }

            const loadingTask = pdfjsLib.getDocument(url);
            this.pdfDoc = await loadingTask.promise;

            // Update Page Count UI if exists
            const pageCountEl = document.getElementById('pdf-page-count');
            if (pageCountEl) pageCountEl.textContent = this.pdfDoc.numPages;

            this.pageNum = initialPage || 1;
            this.renderPage(this.pageNum);

        } catch (error) {
            console.error("PDF Load Error:", error);
            if (error.name !== 'RenderingCancelledException') {
                this.container.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden des PDFs.</div>`;
            }
        }
    }

    renderPage(num) {
        this.pageRendering = true;

        // Fetch page
        this.pdfDoc.getPage(num).then((page) => {
            const viewport = page.getViewport({ scale: this.scale });
            this.canvas.height = viewport.height;
            this.canvas.width = viewport.width;

            const renderContext = {
                canvasContext: this.ctx,
                viewport: viewport
            };

            this.renderTask = page.render(renderContext);

            // Wait for render to finish
            this.renderTask.promise.then(() => {
                this.pageRendering = false;
                if (this.pageNumPending !== null) {
                    this.renderPage(this.pageNumPending);
                    this.pageNumPending = null;
                }
            }).catch(err => {
                // Ignore cancelled
            });
        });

        // Update UI counters
        const pageNumEl = document.getElementById('pdf-page-num');
        if (pageNumEl) pageNumEl.textContent = num;

        // Update Buttons
        document.getElementById('pdf-prev').disabled = num <= 1;
        document.getElementById('pdf-next').disabled = num >= this.pdfDoc.numPages;
    }

    queueRenderPage(num) {
        if (this.pageRendering) {
            this.pageNumPending = num;
        } else {
            this.renderPage(num);
        }
    }

    onPrevPage() {
        if (this.pageNum <= 1) return;
        this.pageNum--;
        this.queueRenderPage(this.pageNum);
    }

    onNextPage() {
        if (this.pageNum >= this.pdfDoc.numPages) return;
        this.pageNum++;
        this.queueRenderPage(this.pageNum);
    }

    show() {
        this.container.classList.remove('hidden');
    }

    hide() {
        this.container.classList.add('hidden');
    }

    destroy() {
        if (this.renderTask) {
            this.renderTask.cancel();
        }
        if (this.pdfDoc) {
            this.pdfDoc.destroy();
        }
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.hide();
    }
}

window.PdfRenderer = PdfRenderer;
