class PdfRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scrollContainer = document.getElementById('pdf-scroll-container');
        this.sidebar = document.getElementById('pdf-sidebar');

        // Initialize state
        this.pdfDoc = null;
        this.scale = 1.5;
        this.renderTask = null;
        this.observer = null;
    }

    async load(url, initialPage = 1) {
        this.show();
        this.scrollContainer.innerHTML = '';
        if (this.sidebar) this.sidebar.innerHTML = '';

        try {
            if (this.renderTask) {
                await this.renderTask.cancel();
            }

            const loadingTask = pdfjsLib.getDocument(url);
            this.pdfDoc = await loadingTask.promise;

            // Update Page Count UI
            const pageCountEl = document.getElementById('pdf-page-count');
            if (pageCountEl) pageCountEl.textContent = this.pdfDoc.numPages;

            // Render Layout
            // 1. Render Main Pages (Full Size)
            await this.renderAllPages();

            // 2. Render Thumbnails (Small Size)
            // We do this non-blocking if possible, or after main render
            this.renderThumbnails();

            // 3. Setup Scroll Spy
            this.setupScrollSpy();

            // Scroll to initial page
            if (initialPage > 1) {
                // Use requestAnimationFrame or slightly longer timeout to ensure layout is ready
                setTimeout(() => this.scrollToPage(initialPage), 800);
            } else {
                this.setActiveThumbnail(1);
            }

        } catch (error) {
            console.error("PDF Load Error:", error);
            if (error.name !== 'RenderingCancelledException') {
                this.scrollContainer.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden des PDFs: ${error.message}</div>`;
            }
        }
    }

    async renderAllPages() {
        // Optimize: Render pages lazily? For now, render all canvas placeholders, then render content.
        for (let num = 1; num <= this.pdfDoc.numPages; num++) {
            await this.renderPage(num);
        }
    }

    async renderPage(num) {
        // Fetch page info
        const page = await this.pdfDoc.getPage(num);
        const viewport = page.getViewport({ scale: this.scale });

        // Create Canvas
        const canvas = document.createElement('canvas');
        canvas.className = 'shadow-md mb-8 mx-auto bg-white'; // Added spacing and background
        canvas.id = `pdf-page-${num}`;
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        // Append to Scroll Container
        this.scrollContainer.appendChild(canvas);

        // Render Content
        const renderContext = {
            canvasContext: canvas.getContext('2d'),
            viewport: viewport
        };
        await page.render(renderContext).promise;
    }

    async renderThumbnails() {
        if (!this.sidebar) return;

        for (let num = 1; num <= this.pdfDoc.numPages; num++) {
            const page = await this.pdfDoc.getPage(num);
            const viewport = page.getViewport({ scale: 0.2 }); // Thumbnail scale

            // Create Container
            const div = document.createElement('div');
            div.className = 'pdf-thumbnail';
            div.id = `pdf-thumb-${num}`;
            div.onclick = () => this.scrollToPage(num);

            // Create Canvas
            const canvas = document.createElement('canvas');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            div.appendChild(canvas);

            // Page Number
            const number = document.createElement('div');
            number.className = 'pdf-thumbnail-number';
            number.textContent = num;
            div.appendChild(number);

            this.sidebar.appendChild(div);

            // Render
            await page.render({
                canvasContext: canvas.getContext('2d'),
                viewport: viewport
            }).promise;
        }
    }

    setupScrollSpy() {
        if (this.observer) this.observer.disconnect();

        const options = {
            root: this.scrollContainer,
            rootMargin: '0px',
            threshold: 0.1 // Trigger when 10% of page is visible
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Start of intersection
                    const pageNum = parseInt(entry.target.id.replace('pdf-page-', ''));
                    this.updateCurrentPageUI(pageNum);
                }
            });
        }, options);

        // Observe all pages
        for (let i = 1; i <= this.pdfDoc.numPages; i++) {
            const page = document.getElementById(`pdf-page-${i}`);
            if (page) this.observer.observe(page);
        }
    }

    updateCurrentPageUI(pageNum) {
        // Update number in toolbar
        const pageNumEl = document.getElementById('pdf-page-num');
        if (pageNumEl) pageNumEl.textContent = pageNum;

        // Sync with global state
        if (typeof ReviewState !== 'undefined') {
            ReviewState.currentPage = pageNum;
        }

        this.setActiveThumbnail(pageNum);
    }

    setActiveThumbnail(num) {
        if (!this.sidebar) return;

        // Remove active class from all
        const allThumbs = this.sidebar.querySelectorAll('.pdf-thumbnail');
        allThumbs.forEach(el => el.classList.remove('active'));

        // Add to current
        const activeThumb = document.getElementById(`pdf-thumb-${num}`);
        if (activeThumb) {
            activeThumb.classList.add('active');
            // Ensure thumbnail is visible in sidebar
            activeThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    scrollToPage(num) {
        const pageCanvas = document.getElementById(`pdf-page-${num}`);
        if (pageCanvas) {
            pageCanvas.scrollIntoView({ behavior: 'auto', block: 'start' });
            // 'auto' is instant, 'smooth' can be slow if jumping far. 'start' aligns top.
            this.updateCurrentPageUI(num);
        }
    }

    // Toolbar "Prev/Next" buttons can blindly call this
    changePage(offset) {
        const currentText = document.getElementById('pdf-page-num').textContent;
        const current = parseInt(currentText) || 1;
        const target = current + offset;
        if (target >= 1 && target <= this.pdfDoc.numPages) {
            this.scrollToPage(target);
        }
    }

    show() {
        this.container.classList.remove('hidden');
        this.container.classList.add('flex'); // Ensure flex layout works
    }

    hide() {
        this.container.classList.add('hidden');
        this.container.classList.remove('flex');
    }

    destroy() {
        this.hide();
        this.scrollContainer.innerHTML = '';
        if (this.sidebar) this.sidebar.innerHTML = '';
        if (this.observer) this.observer.disconnect();
    }
}

// Global helper for toolbar buttons
window.changePdfPage = (offset) => {
    // Assuming we can access the active renderer instance or via DOM
    // For now, simpler to hook into the global functionality if ReviewState exposes it,
    // or we can attach the method to the window if this instance is singleton-like for the view.
    // Ideally, DocumentViewer.js should handle this.
    // But since the template calls `changePdfPage`, let's define it here or rely on DocumentViewer.
};

window.PdfRenderer = PdfRenderer;
