class XlsxRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.workbook = null;
        this.activeSheet = null;
    }

    async load(url) {
        this.show();
        this.container.innerHTML = '<div class="flex justify-center p-4"><div class="animate-spin h-6 w-6 border-2 border-green-500 rounded-full border-t-transparent"></div></div>';

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Load failed");
            const arrayBuffer = await response.arrayBuffer();

            this.workbook = XLSX.read(arrayBuffer, { type: 'array' });
            if (!this.workbook.SheetNames.length) throw new Error("Keine Tabellenblätter gefunden.");

            this.activeSheet = this.workbook.SheetNames[0];
            this.renderUI();

        } catch (error) {
            console.error("XLSX Load Error:", error);
            this.container.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden der Tabelle: ${error.message}</div>`;
        }
    }

    renderUI() {
        // Tab Container
        const tabContainer = document.createElement('div');
        tabContainer.className = 'flex border-b border-gray-200 mb-2 overflow-x-auto';

        this.workbook.SheetNames.forEach(name => {
            const btn = document.createElement('button');
            btn.className = `px-4 py-2 text-sm font-medium whitespace-nowrap ${name === this.activeSheet ? 'text-green-600 border-b-2 border-green-600' : 'text-gray-500 hover:text-gray-700'}`;
            btn.textContent = name;
            btn.onclick = () => {
                this.activeSheet = name;
                this.renderUI(); // Re-render to update tabs and content
            };
            tabContainer.appendChild(btn);
        });

        // Content Container
        const contentContainer = document.createElement('div');
        contentContainer.className = 'bg-white shadow rounded overflow-auto p-4 max-h-[calc(100vh-250px)]';

        // Render Sheet HTML
        const worksheet = this.workbook.Sheets[this.activeSheet];
        const html = XLSX.utils.sheet_to_html(worksheet, {
            className: 'min-w-full divide-y divide-gray-200 table-auto text-sm'
        });

        contentContainer.innerHTML = `
            <style>
                table { border-collapse: collapse; width: 100%; white-space: nowrap; }
                td, th { border: 1px solid #e5e7eb; padding: 4px 8px; }
            </style>
            ${html}
        `;

        this.container.innerHTML = '';
        this.container.appendChild(tabContainer);
        this.container.appendChild(contentContainer);
    }

    show() {
        this.container.classList.remove('hidden');
    }

    hide() {
        this.container.classList.add('hidden');
    }

    destroy() {
        this.container.innerHTML = '';
        this.workbook = null;
        this.hide();
    }
}

window.XlsxRenderer = XlsxRenderer;
