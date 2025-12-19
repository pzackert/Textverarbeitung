// Chat functionality for the review cockpit
// Handles sending messages to the AI assistant via API

class ChatManager {
    constructor(projectId) {
        this.projectId = projectId;
        this.chatContainer = document.getElementById('chat-messages');
        this.form = null;
        this.initialized = false;
    }

    init() {
        // Find the chat form
        const forms = document.querySelectorAll('form[hx-post*="/chat"]');
        if (forms.length > 0) {
            this.form = forms[0];

            // Override HTMX behavior - handle ourselves
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                e.stopPropagation();

                const messageInput = this.form.querySelector('input[name="message"]');
                if (messageInput && messageInput.value.trim()) {
                    this.sendMessage(messageInput.value.trim());
                    messageInput.value = '';
                }

                return false;
            });

            this.initialized = true;
            console.log('Chat manager initialized');
        }
    }

    async sendMessage(message) {
        if (!this.chatContainer) {
            console.error('Chat container not found');
            return;
        }

        // Add user message to UI
        this.appendMessage('user', message);

        // Show loading indicator
        this.showLoadingIndicator();

        try {
            // Call API
            const response = await fetch(`/api/projects/${this.projectId}/chat/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    include_rag: true
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            // Hide loading indicator
            this.hideLoadingIndicator();

            // Add assistant message
            this.appendMessage('assistant', data.response, data.sources);

        } catch (error) {
            console.error('Chat error:', error);
            this.hideLoadingIndicator();
            this.appendMessage('assistant', `Fehler: ${error.message}. Bitte versuchen Sie es erneut.`);
        }

        // Scroll to bottom
        this.scrollToBottom();
    }

    appendMessage(role, content, sources = []) {
        if (!this.chatContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `flex w-full ${role === 'user' ? 'justify-end' : 'justify-start'}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `max-w-[85%] rounded-lg px-4 py-2 shadow-sm ${role === 'user'
                ? 'bg-blue-600 text-white rounded-br-none'
                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none prose prose-sm'
            }`;

        // Add message content
        if (role === 'user') {
            bubbleDiv.textContent = content;
        } else {
            // Assistant message - may contain HTML
            bubbleDiv.innerHTML = content;

            // Add sources if available
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'mt-3 pt-3 border-t border-gray-200';
                sourcesDiv.innerHTML = '<p class="text-xs font-semibold text-gray-500 mb-2">Quellen:</p>';

                const sourcesList = document.createElement('div');
                sourcesList.className = 'flex flex-wrap gap-2';

                sources.forEach((source, idx) => {
                    const sourceLink = document.createElement('button');
                    sourceLink.className = 'text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors';
                    sourceLink.textContent = `${source.document}${source.page ? ` (S. ${source.page})` : ''}`;
                    sourceLink.onclick = () => {
                        // Open document when clicked
                        if (window.renderDocument) {
                            window.renderDocument(source.document);
                        }
                    };
                    sourcesList.appendChild(sourceLink);
                });

                sourcesDiv.appendChild(sourcesList);
                bubbleDiv.appendChild(sourcesDiv);
            }
        }

        messageDiv.appendChild(bubbleDiv);
        this.chatContainer.appendChild(messageDiv);
    }

    showLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.classList.remove('htmx-indicator');
            indicator.style.display = 'flex';
        }
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.style.display = 'none';
            indicator.classList.add('htmx-indicator');
        }
    }

    scrollToBottom() {
        if (this.chatContainer) {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    const projectId = window.location.pathname.split('/')[2];
    if (projectId) {
        window.chatManager = new ChatManager(projectId);

        // Small delay to ensure HTMX has loaded
        setTimeout(() => {
            window.chatManager.init();
        }, 100);
    }
});
