// Main JavaScript for IFB PROFI Platform

document.addEventListener('DOMContentLoaded', () => {
    console.log('IFB Platform initialized');

    // Global HTMX Configuration
    document.body.addEventListener('htmx:beforeSwap', function(evt) {
        // Allow 422 and 400 responses to swap (for form validation errors)
        if (evt.detail.xhr.status === 422 || evt.detail.xhr.status === 400) {
            evt.detail.shouldSwap = true;
            evt.detail.isError = false;
        }
    });

    // Global Toast Notification Handler (example)
    window.showToast = function(message, type = 'info') {
        // Implementation for a simple toast
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg text-white transition-opacity duration-300 ${
            type === 'error' ? 'bg-red-500' : 
            type === 'success' ? 'bg-green-500' : 'bg-blue-500'
        }`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
