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

            if (!response.ok) {
                let errorMsg = `API error: ${response.status}`;
                try {
                    const errData = await response.json();
                    if (errData.detail) errorMsg = errData.detail;
                } catch (e) { /* ignore JSON parse error */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            this.hideLoadingIndicator();

            const msg = data.assistant_message;
            this.appendMessage('assistant', msg.content, msg.sources, msg.metrics);

        } catch (error) {
            console.error('Chat error:', error);
            this.hideLoadingIndicator();
            this.appendMessage('assistant', `**Fehler:** ${error.message}`);
        }

        this.scrollToBottom();
    }

    toggleSources(isVisible) {
        const sourceContainers = this.chatContainer.querySelectorAll('.source-container');
        sourceContainers.forEach(el => {
            el.style.display = isVisible ? 'block' : 'none';
        });
        this.sourcesVisible = isVisible;
    }

    appendMessage(role, content, sources = [], metrics = null) {
        if (!this.chatContainer) return;

        const wrapperDiv = document.createElement('div');
        wrapperDiv.className = `w-full max-w-4xl mx-auto flex gap-4 anim-fade-in ${role === 'user' ? 'justify-end' : 'justify-start'} mb-6`;

        // 1. Avatar
        if (role === 'assistant') {
            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center flex-shrink-0 text-white shadow-md';
            avatarDiv.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`;
            wrapperDiv.appendChild(avatarDiv);
        }

        // 2. Message Column
        const msgColHandler = document.createElement('div');
        msgColHandler.className = `flex flex-col max-w-[85%] ${role === 'user' ? 'items-end' : 'items-start'}`;

        // Name Label
        const nameLabel = document.createElement('span');
        nameLabel.className = 'text-xs font-bold text-gray-400 mb-1 ml-1';
        nameLabel.textContent = role === 'user' ? 'Du' : 'IFB Assistent';
        msgColHandler.appendChild(nameLabel);

        // Content Bubble
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = `px-4 py-3 rounded-2xl shadow-sm text-base leading-relaxed overflow-hidden ${role === 'user'
            ? 'bg-blue-600 text-white rounded-br-none'
            : 'bg-gray-50 border border-gray-200 text-gray-800 rounded-bl-none prose prose-blue max-w-none'}`;

        // Text Content
        const contentDiv = document.createElement('div');
        if (role === 'user') {
            contentDiv.textContent = content;
            contentDiv.className = 'whitespace-pre-wrap';
        } else {
            // Render Markdown if available
            contentDiv.innerHTML = window.marked ? marked.parse(content) : content.replace(/\n/g, '<br>');
        }
        bubbleDiv.appendChild(contentDiv);

        // Metrics Display (Both roles if available, usually assistant)
        if (metrics) {
            const metricsDiv = document.createElement('div');
            metricsDiv.className = `mt-2 text-[10px] opacity-70 flex gap-2 border-t border-black/10 pt-1 ${role === 'user' ? 'text-blue-100' : 'text-gray-400'}`;
            metricsDiv.innerHTML = `
                <span>${Math.round((metrics.tokens_per_second || 0) * 100) / 100} tok/sec</span>
                <span>•</span>
                <span>${metrics.total_tokens || 0} tokens</span>
                <span>•</span>
                <span>${Math.round((metrics.duration_seconds || 0) * 100) / 100}s</span>
            `;
            bubbleDiv.appendChild(metricsDiv);
        }

        // Sources (Only for Project Chat - Assistant)
        // Check visibility state (default true)
        if (role === 'assistant' && sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'source-container mt-4 pt-3 border-t border-gray-200/50';
            if (this.sourcesVisible === false) sourcesDiv.style.display = 'none';

            sourcesDiv.innerHTML = '<p class="text-xs font-bold mb-2 uppercase opacity-70 tracking-wider">Quellen:</p>';

            const sourcesList = document.createElement('div');
            sourcesList.className = 'flex flex-wrap gap-2';

            sources.forEach((source) => {
                const docName = source.doc_name || source.document || source.filename || source.source || 'Dokument';
                const page = source.page;
                // Using metadata if available for more robustness
                const metaName = (source.metadata && source.metadata.doc_name) || docName;
                const metaPage = (source.metadata && source.metadata.page) || page;

                const sourceItem = document.createElement('div');
                sourceItem.className = 'text-xs bg-white/80 backdrop-blur px-2.5 py-1.5 rounded-md border border-gray-200 shadow-sm flex items-center gap-1.5 max-w-[200px] cursor-pointer hover:bg-gray-50 transition-colors';
                sourceItem.title = "Klicken zum Öffnen";
                sourceItem.innerHTML = `
                    <span class="opacity-50">📄</span>
                    <span class="truncate">${metaName}</span>
                    ${metaPage ? `<span class="opacity-60 text-[10px]">S.${metaPage}</span>` : ''}
                `;

                // Click handler for PDF Viewer
                sourceItem.onclick = () => {
                    if (window.renderDocument) {
                        window.renderDocument(metaName, metaPage);
                    } else if (window.loadDocument) {
                        window.loadDocument(metaName, 'original', metaPage || 1);
                    }
                };

                sourcesList.appendChild(sourceItem);
            });
            sourcesDiv.appendChild(sourcesList);
            bubbleDiv.appendChild(sourcesDiv);
        }

        msgColHandler.appendChild(bubbleDiv);
        wrapperDiv.appendChild(msgColHandler);

        // 3. User Avatar (Right side)
        if (role === 'user') {
            const userAvatar = document.createElement('div');
            userAvatar.className = 'w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 text-gray-500 ml-4'; // Added margin-left
            userAvatar.innerHTML = `<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`;
            wrapperDiv.appendChild(userAvatar);
        }

        this.chatContainer.appendChild(wrapperDiv);
    }

    showLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.classList.remove('hidden');
            indicator.style.display = 'flex'; // Ensure flex layout
            // z-index fix if needed, but it's in flow.
            this.scrollToBottom();
        }
    }

    hideLoadingIndicator() {
        const indicator = document.getElementById('thinking-indicator');
        if (indicator) {
            indicator.style.display = 'none';
            indicator.classList.add('hidden');
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
