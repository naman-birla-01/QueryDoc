class ChatInterface {
    constructor(api) {
        this.api = api;
        
        this.form = document.getElementById('chat-form');
        this.input = document.getElementById('chat-input');
        this.submitBtn = document.getElementById('chat-submit');
        this.history = document.getElementById('chat-history');
        this.docFilterSelect = document.getElementById('doc-filter-select');

        this.initEventListeners();
    }

    initEventListeners() {
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleQuery();
        });

        // Toggle submit button based on input
        this.input.addEventListener('input', () => {
            const val = this.input.value.trim();
            // Assuming documents exist if input is not disabled
            if (!this.input.disabled) {
                this.submitBtn.disabled = val.length === 0;
            }
        });
    }

    async handleQuery() {
        const question = this.input.value.trim();
        if (!question) return;

        const documentId = this.docFilterSelect.value || null;

        // Clear welcome message if present
        const welcome = this.history.querySelector('.welcome-message');
        if (welcome) welcome.remove();

        // Add user message
        this.appendMessage('user', question);
        this.input.value = '';
        this.submitBtn.disabled = true;

        // Add loading indicator
        const loadingId = this.appendLoading();

        try {
            const response = await this.api.query(question, documentId);
            this.removeLoading(loadingId);
            this.appendMessage('ai', response.answer, response.sources);
        } catch (error) {
            this.removeLoading(loadingId);
            this.appendMessage('ai', `Error: ${error.message}. Please make sure the backend is running and you have uploaded documents.`);
        } finally {
            // Scroll to bottom
            this.history.scrollTop = this.history.scrollHeight;
        }
    }

    appendMessage(role, content, sources = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        // Basic markdown-like formatting for AI responses (bold, linebreaks)
        let formattedContent = role === 'ai' ? this.formatText(content) : content;

        let html = `<div class="message-content">${formattedContent}</div>`;
        
        if (sources && sources.length > 0) {
            html += `
                <div class="sources-container">
                    <button class="sources-toggle">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                        View Sources (${sources.length})
                    </button>
                    <div class="sources-list">
                        ${sources.map((s, i) => `
                            <div class="source-item">
                                <div class="source-header">
                                    <span>Source ${i + 1} • ${s.filename} (Page ${s.page_number})</span>
                                    <span>Score: ${(s.relevance_score * 100).toFixed(0)}%</span>
                                </div>
                                <div class="source-text">${s.text.substring(0, 200)}...</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        msgDiv.innerHTML = html;
        this.history.appendChild(msgDiv);

        // Add toggle listener for sources
        if (sources && sources.length > 0) {
            const toggle = msgDiv.querySelector('.sources-toggle');
            const list = msgDiv.querySelector('.sources-list');
            toggle.addEventListener('click', () => {
                list.classList.toggle('show');
                if (list.classList.contains('show')) {
                    toggle.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6"/></svg> Hide Sources`;
                } else {
                    toggle.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg> View Sources (${sources.length})`;
                }
            });
        }
        
        this.history.scrollTop = this.history.scrollHeight;
    }

    appendLoading() {
        const id = 'loading-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ai`;
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        this.history.appendChild(msgDiv);
        this.history.scrollTop = this.history.scrollHeight;
        return id;
    }

    removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    formatText(text) {
        // Convert simple **bold** and newlines
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');
        return formatted;
    }
}
