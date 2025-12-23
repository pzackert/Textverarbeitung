/**
 * ReviewState.js
 * managing the current state of the document viewer
 */
const ReviewState = {
    projectId: null,
    currentDocument: null, // { filename, format, originalUrl, annotatedUrl, hasAnnotated }
    currentView: 'original', // 'original' | 'annotated'
    currentPage: 1,
    scale: 1.25,

    // Listeners
    listeners: [],

    subscribe(callback) {
        this.listeners.push(callback);
    },

    notify() {
        this.listeners.forEach(cb => cb(this));
    },

    setDocument(doc) {
        this.currentDocument = doc;
        this.currentView = doc.hasAnnotated ? 'annotated' : 'original'; // Default to annotated if available? No, usually original first unless configured. Analysis says "Toggle between Original and Annotated". Let's Default to Original.
        this.currentView = 'original';
        this.currentPage = 1;
        this.notify();
    },

    setView(viewMode) {
        if (viewMode === 'annotated' && !this.currentDocument?.hasAnnotated) return;
        this.currentView = viewMode;
        this.notify(); // Viewers should react to this
    },

    setPage(pageNum) {
        this.currentPage = pageNum;
        // Don't notify full reload, just let viewer handle it if possible, 
        // but for now simple notification is safer to sync UI
    }
};

window.ReviewState = ReviewState;
