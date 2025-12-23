// Chat functionality for the review cockpit
// Handles sending messages to the AI assistant via API

class ChatManager {
    constructor(projectId) {
        this.projectId = projectId;
        this.chatContainer = document.getElementById('chat-messages');
        this.form = null;
        this.initialized = false;
    }

    async init() {
        // Find the chat form - generic selector
        this.form = document.querySelector('div.review-assistant form');

        if (this.form) {
            // Remove HTMX attributes to prevent double submission/htmx interference if possible, 
            // or just rely on preventDefault.
            this.form.removeAttribute('hx-post');

            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                e.stopImmediatePropagation(); // Stop HTMX from firing if attached
                const messageInput = this.form.querySelector('input[name="message"]');
                if (messageInput && messageInput.value.trim()) {
                    this.sendMessage(messageInput.value.trim());
                    messageInput.value = '';
                }
            });
        }

        this.initialized = true;

        // Use Case B1: Load History
        await this.loadHistory();
    }

    async loadHistory() {
        if (!this.chatContainer) return;

        try {
            const res = await fetch(`/api/chats/project/${this.projectId}`);
            if (!res.ok) {
                if (res.status === 404) return;
                throw new Error("Failed to load history");
            }
            const data = await res.json();
            const messages = data.messages || [];

            if (messages.length > 0) {
                this.chatContainer.innerHTML = '';
                messages.forEach(msg => {
                    const sources = msg.sources || [];
                    this.appendMessage(msg.role, msg.content, sources, msg.metrics);
                });
                this.scrollToBottom();
            }
        } catch (e) {
            console.error("History load error:", e);
        }
    }

    async sendMessage(message) {
        if (!this.chatContainer) return;

        this.appendMessage('user', message);
        this.showLoadingIndicator();

        try {
            // Use Case B2: Send Message
            const response = await fetch(`/api/chats/project/${this.projectId}/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    include_rag: true
                })
            });

            if (!response.ok) throw new Error(`API error: ${response.status}`);

            const data = await response.json();
            this.hideLoadingIndicator();

            const msg = data.assistant_message;
            this.appendMessage('assistant', msg.content, msg.sources, msg.metrics);

        } catch (error) {
            console.error('Chat error:', error);
            this.hideLoadingIndicator();
            this.appendMessage('assistant', `Fehler: ${error.message}. Bitte versuchen Sie es erneut.`);
        }

        this.scrollToBottom();
    }

    appendMessage(role, content, sources = [], metrics = null) {
        if (!this.chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `flex w-full ${role === 'user' ? 'justify-end' : 'justify-start'} mb-4`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `max-w-[85%] rounded-lg px-4 py-2 shadow-sm ${role === 'user'
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none prose prose-sm'
            }`;

        if (role === 'user') {
            bubbleDiv.textContent = content;
        } else {
            // Simple newline handling
            bubbleDiv.innerHTML = content.replace(/\n/g, '<br>');

            // Sources
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'mt-3 pt-3 border-t border-gray-200';
                sourcesDiv.innerHTML = '<p class="text-xs font-semibold text-gray-500 mb-2">Quellen:</p>';

                const sourcesList = document.createElement('div');
                sourcesList.className = 'flex flex-wrap gap-2';

                sources.forEach((source) => {
                    const docName = source.document || source.doc_name || 'Dokument';
                    const page = source.page;

                    const sourceLink = document.createElement('button');
                    sourceLink.className = 'text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors border border-blue-200';
                    sourceLink.textContent = `${docName}${page ? ` (S. ${page})` : ''}`;
                    sourceLink.type = 'button';
                    sourceLink.onclick = () => {
                        if (window.renderDocument) {
                            window.renderDocument(docName);
                        }
                    };
                    sourcesList.appendChild(sourceLink);
                });

                sourcesDiv.appendChild(sourcesList);
                bubbleDiv.appendChild(sourcesDiv);
            }

            // Metrics
            if (metrics) {
                const metricsDiv = document.createElement('div');
                metricsDiv.className = 'mt-1 pt-1 border-t border-gray-100 opacity-60 text-[10px] font-mono flex gap-2 text-gray-500';
                metricsDiv.innerHTML = `
                    <span>${metrics.tokens_per_second || 0} tok/s</span>
                    <span>•</span>
                    <span>${metrics.total_tokens || 0} tokens</span>
                 `;
                bubbleDiv.appendChild(metricsDiv);
            }
        }

        messageDiv.appendChild(bubbleDiv);
        this.chatContainer.appendChild(messageDiv);
    }

    showLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.classList.remove('hidden');
            indicator.style.display = 'flex';
            // Force redraw?
            indicator.offsetHeight;
        }
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.style.display = 'none';
            indicator.classList.add('hidden'); // Fix: Add back hidden class
        }
    }

    scrollToBottom() {
        if (this.chatContainer) {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const pathParts = window.location.pathname.split('/');
    if (pathParts[1] === 'projects' && pathParts[2]) {
        // Only on project pages
        const projectId = pathParts[2];

        // Wait for Alpine/Layout
        setTimeout(() => {
            window.chatManager = new ChatManager(projectId);
            window.chatManager.init();
        }, 300);
    }
});
