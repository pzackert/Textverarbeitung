// Review Cockpit Logic - Native Browser Viewer

let currentDocState = {
    projectId: null,
    filename: null,
    originalUrl: null,
    annotatedUrl: null,
    currentView: 'original' // 'original' or 'annotated'
};

// Global function to be called from templates
window.renderPDF = function(filename) {
    const projectId = window.location.pathname.split('/')[2];
    
    currentDocState.projectId = projectId;
    currentDocState.filename = filename;
    currentDocState.originalUrl = `/projects/${projectId}/files/${filename}`;
    currentDocState.annotatedUrl = `/projects/${projectId}/files/annotated_${filename}`;
    currentDocState.currentView = 'original'; // Reset to original on new doc load
    
    updateViewer();
    updateToggleUI();
};

window.toggleView = function(mode) {
    if (currentDocState.currentView === mode) return;
    
    currentDocState.currentView = mode;
    updateViewer();
    updateToggleUI();
};

function updateViewer() {
    const viewerFrame = document.getElementById('doc-viewer-frame');
    const placeholder = document.getElementById('viewer-placeholder');
    const nameLabel = document.getElementById('current-doc-name');
    const downloadLink = document.getElementById('download-link');
    const toggleContainer = document.getElementById('view-toggle-container');
    
    if (!viewerFrame) return;

    const isPdf = currentDocState.filename && currentDocState.filename.toLowerCase().endsWith('.pdf');
    
    const url = currentDocState.currentView === 'annotated' 
        ? currentDocState.annotatedUrl 
        : currentDocState.originalUrl;

    // Update UI
    if (nameLabel) nameLabel.textContent = currentDocState.filename + (currentDocState.currentView === 'annotated' ? ' (Annotiert)' : '');
    
    if (downloadLink) {
        downloadLink.href = url;
        downloadLink.classList.remove('hidden');
    }

    if (isPdf) {
        // Hide placeholder, show frame
        if (placeholder) placeholder.style.display = 'none';
        viewerFrame.style.display = 'block';
        if (toggleContainer) toggleContainer.classList.remove('hidden');

        // Set source
        console.log(`Loading document (${currentDocState.currentView}): ${url}`);
        viewerFrame.src = url;
    } else {
        // Show placeholder for non-PDFs
        viewerFrame.style.display = 'none';
        viewerFrame.src = 'about:blank';
        if (toggleContainer) toggleContainer.classList.add('hidden');
        
        if (placeholder) {
            placeholder.style.display = 'flex';
            placeholder.innerHTML = `
                <div class="flex flex-col items-center justify-center h-full text-gray-500">
                    <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    <p class="text-lg font-medium">Vorschau nicht verfügbar</p>
                    <p class="text-sm mt-2">Bitte nutzen Sie den Download-Button.</p>
                </div>
            `;
        }
    }
}

function updateToggleUI() {
    const container = document.getElementById('view-toggle-container');
    const btnOriginal = document.getElementById('btn-original');
    const btnAnnotated = document.getElementById('btn-annotated');
    
    if (!container || !btnOriginal || !btnAnnotated) return;
    
    // Show toggle container
    container.classList.remove('hidden');
    
    // Update button styles
    if (currentDocState.currentView === 'original') {
        btnOriginal.className = "px-3 py-1 text-xs font-medium rounded-md bg-white shadow-sm text-gray-800 transition-all";
        btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded-md text-gray-500 hover:text-gray-700 transition-all";
    } else {
        btnOriginal.className = "px-3 py-1 text-xs font-medium rounded-md text-gray-500 hover:text-gray-700 transition-all";
        btnAnnotated.className = "px-3 py-1 text-xs font-medium rounded-md bg-white shadow-sm text-gray-800 transition-all";
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Review Cockpit initialized (Native Viewer + Toggle)');
});
