class DocumentManager {
    constructor(api, state) {
        this.api = api;
        this.state = state;
        
        this.uploadZone = document.getElementById('upload-zone');
        this.fileInput = document.getElementById('file-input');
        this.documentList = document.getElementById('document-list');
        this.uploadProgress = document.getElementById('upload-progress');
        this.docFilterSelect = document.getElementById('doc-filter-select');

        this.initEventListeners();
        this.loadDocuments();
    }

    initEventListeners() {
        // Click to upload
        this.uploadZone.addEventListener('click', () => this.fileInput.click());
        
        // File selection
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        this.uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadZone.classList.add('dragover');
        });

        this.uploadZone.addEventListener('dragleave', () => {
            this.uploadZone.classList.remove('dragover');
        });

        this.uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleUpload(e.dataTransfer.files[0]);
            }
        });
    }

    async handleUpload(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert('Only PDF files are supported.');
            return;
        }

        this.uploadZone.style.display = 'none';
        this.uploadProgress.classList.remove('hidden');

        try {
            await this.api.uploadDocument(file);
            await this.loadDocuments();
            // Clear input so same file can be uploaded again if needed
            this.fileInput.value = '';
        } catch (error) {
            alert(`Upload failed: ${error.message}`);
        } finally {
            this.uploadProgress.classList.add('hidden');
            this.uploadZone.style.display = 'flex';
        }
    }

    async loadDocuments() {
        try {
            const data = await this.api.listDocuments();
            this.state.documents = data.documents;
            this.renderDocumentList();
            this.updateDocumentFilter();
            
            // Enable/disable chat based on docs
            const hasDocs = data.documents.length > 0;
            document.getElementById('chat-input').disabled = !hasDocs;
            document.getElementById('chat-submit').disabled = !hasDocs;
            
            if (hasDocs) {
                document.getElementById('chat-input').placeholder = "Ask a question...";
            } else {
                document.getElementById('chat-input').placeholder = "Upload a document first...";
            }
            
        } catch (error) {
            console.error('Failed to load documents:', error);
            this.documentList.innerHTML = `<p style="color:var(--danger);font-size:0.9rem;padding:0.5rem">Failed to connect to server. Is backend running?</p>`;
        }
    }

    renderDocumentList() {
        this.documentList.innerHTML = '';
        
        if (this.state.documents.length === 0) {
            this.documentList.innerHTML = `<p style="color:var(--text-secondary);font-size:0.9rem;text-align:center;padding:1rem;">No documents uploaded yet.</p>`;
            return;
        }

        this.state.documents.forEach(doc => {
            const div = document.createElement('div');
            div.className = 'document-item';
            div.innerHTML = `
                <div class="doc-info">
                    <div class="doc-name" title="${doc.filename}">${doc.filename}</div>
                    <div class="doc-meta">${doc.total_chunks} chunks</div>
                </div>
                <button class="delete-btn" data-id="${doc.document_id}" title="Delete">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
            `;
            
            const deleteBtn = div.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => this.deleteDocument(doc.document_id));
            
            this.documentList.appendChild(div);
        });
    }

    updateDocumentFilter() {
        // Keep the first option
        const firstOption = this.docFilterSelect.options[0];
        this.docFilterSelect.innerHTML = '';
        this.docFilterSelect.appendChild(firstOption);
        
        this.state.documents.forEach(doc => {
            const option = document.createElement('option');
            option.value = doc.document_id;
            option.textContent = doc.filename;
            this.docFilterSelect.appendChild(option);
        });
    }

    async deleteDocument(id) {
        if (!confirm('Are you sure you want to delete this document?')) return;
        
        try {
            await this.api.deleteDocument(id);
            // If the deleted document was selected in filter, reset filter
            if (this.docFilterSelect.value === id) {
                this.docFilterSelect.value = '';
            }
            await this.loadDocuments();
        } catch (error) {
            alert(`Delete failed: ${error.message}`);
        }
    }
}
