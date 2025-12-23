class DocxRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    async load(url) {
        this.show();
        this.container.innerHTML = '<div class="flex justify-center p-4"><div class="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div></div>';

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Load failed");
            const arrayBuffer = await response.arrayBuffer();

            const result = await mammoth.convertToHtml({ arrayBuffer: arrayBuffer });

            // Render HTML
            this.container.innerHTML = `<div class="prose prose-sm max-w-none bg-white p-8 shadow rounded min-h-[500px]">${result.value}</div>`;

        } catch (error) {
            console.error("DOCX Load Error:", error);
            this.container.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden des Dokuments: ${error.message}</div>`;
        }
    }

    show() {
        this.container.classList.remove('hidden');
    }

    hide() {
        this.container.classList.add('hidden');
    }

    destroy() {
        this.container.innerHTML = '';
        this.hide();
    }
}

window.DocxRenderer = DocxRenderer;
