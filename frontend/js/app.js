// Global State
const appState = {
    documents: []
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize components
    const docManager = new DocumentManager(api, appState);
    const chatInterface = new ChatInterface(api);
});
