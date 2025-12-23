class XlsxRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    async load(url) {
        this.show();
        this.container.innerHTML = '<div class="flex justify-center p-4"><div class="animate-spin h-6 w-6 border-2 border-green-500 rounded-full border-t-transparent"></div></div>';

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Load failed");
            const arrayBuffer = await response.arrayBuffer();

            const workbook = XLSX.read(arrayBuffer, { type: 'array' });
            if (!workbook.SheetNames.length) throw new Error("Keine Tabellenblätter gefunden.");

            // Render first sheet
            const worksheet = workbook.Sheets[workbook.SheetNames[0]];
            const html = XLSX.utils.sheet_to_html(worksheet, {
                className: 'min-w-full divide-y divide-gray-200 table-auto'
            });

            this.container.innerHTML = `
                <div class="bg-white shadow rounded overflow-auto p-4 max-h-[calc(100vh-200px)]">
                    <style>
                        table { border-collapse: collapse; width: 100%; }
                        td, th { border: 1px solid #e5e7eb; padding: 4px 8px; font-size: 0.875rem; }
                        iframe { width: 100%; min-height: 500px; }
                    </style>
                    ${html}
                </div>`;

        } catch (error) {
            console.error("XLSX Load Error:", error);
            this.container.innerHTML = `<div class="text-red-500 p-4">Fehler beim Laden der Tabelle: ${error.message}</div>`;
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

window.XlsxRenderer = XlsxRenderer;
