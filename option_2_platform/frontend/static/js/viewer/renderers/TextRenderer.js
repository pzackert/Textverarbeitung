class TextRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    async load(url) {
        this.show();
        this.container.innerHTML = '<div class="flex justify-center p-4">Lade Text...</div>';

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Load failed");
            const text = await response.text();

            this.container.innerHTML = `
                <div class="bg-white shadow rounded p-4 overflow-auto max-h-[calc(100vh-200px)]">
                    <pre class="font-mono text-xs whitespace-pre-wrap text-gray-800">${text.replace(/</g, '&lt;')}</pre>
                </div>`;

        } catch (error) {
            console.error("Text Load Error:", error);
            this.container.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden: ${error.message}</div>`;
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

window.TextRenderer = TextRenderer;
