const API_BASE = 'http://localhost:8080/api/v1';

const api = {
    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        return response.json();
    },

    async listDocuments() {
        const response = await fetch(`${API_BASE}/documents/`);
        if (!response.ok) throw new Error('Failed to fetch documents');
        return response.json();
    },

    async deleteDocument(documentId) {
        const response = await fetch(`${API_BASE}/documents/${documentId}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error('Failed to delete document');
        return response.json();
    },

    async query(question, documentId = null) {
        const payload = { question, top_k: 5 };
        if (documentId) {
            payload.document_id = documentId;
        }

        const response = await fetch(`${API_BASE}/query/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }
        return response.json();
    }
};
