// Main JavaScript for IFB PROFI Platform

document.addEventListener('DOMContentLoaded', () => {
    console.log('IFB Platform initialized');

    // Global HTMX Configuration
    document.body.addEventListener('htmx:beforeSwap', function (evt) {
        // Allow 422 and 400 responses to swap (for form validation errors)
        if (evt.detail.xhr.status === 422 || evt.detail.xhr.status === 400) {
            evt.detail.shouldSwap = true;
            evt.detail.isError = false;
        }
    });

    // Global Toast Notification Handler (example)
    window.showToast = function (message, type = 'info') {
        // Implementation for a simple toast
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg text-white transition-opacity duration-300 ${type === 'error' ? 'bg-red-500' :
            type === 'success' ? 'bg-green-500' : 'bg-blue-500'
            }`;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Surface startup status (ready/degraded) after redirect from startup page
    const startupStatus = sessionStorage.getItem('startupStatus');
    if (startupStatus) {
        try {
            const parsed = JSON.parse(startupStatus);
            const type = parsed.status === 'degraded' ? 'error' : 'success';
            const msg = parsed.message || (parsed.status === 'degraded' ? 'System im Degraded Mode' : 'System bereit');
            window.showToast(msg, type);
        } catch (e) {
            console.warn('Failed to parse startup status', e);
        } finally {
            sessionStorage.removeItem('startupStatus');
        }
    }
    // Global System Restart Handler
    window.triggerSystemRestart = async function (event) {
        if (event) event.preventDefault();

        console.log("Triggering system restart...");
        const overlay = document.getElementById('system-loading-overlay');
        if (overlay) overlay.style.display = 'flex';

        try {
            // Trigger backend startup
            const res = await fetch('/api/system/startup', { method: 'POST' });
            if (!res.ok) throw new Error("Startup trigger failed");

            // Poll for completion or simple reload after delay
            // Since the startup might take time, we reload to the root which (via middleware) should show startup if not ready
            // OR we just wait a bit.
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);

        } catch (e) {
            console.error(e);
            alert("Fehler beim Neustart: " + e.message);
            if (overlay) overlay.style.display = 'none';
        }
    };
    // Batch Check All Projects
    window.checkAllProjects = async function () {
        if (!confirm("Möchten Sie wirklich ALLE Anträge gegen ALLE Kriterien prüfen lassen? Dies kann einige Zeit dauern.")) return;

        try {
            showToast("Starte Batch-Prüfung...", "info");
            const res = await fetch('/api/queue/projects/all/criteria/all', { method: 'POST' });
            if (!res.ok) throw new Error("API call failed");
            const data = await res.json();
            showToast(`Prüfung gestartet: ${data.jobs.length} Anträge in der Warteschlange.`, "success");
        } catch (e) {
            console.error(e);
            showToast("Fehler beim Starten der Batch-Prüfung.", "error");
        }
    };
});
