/**
 * Niscahya Chatbot API Client
 * Helper untuk integrasi dengan website utama
 *
 * Usage:
 * const chatbot = new NiscahyaChatbot('http://localhost:8000');
 * const response = await chatbot.sendMessage('Halo, apa produk PJUTS tersedia?');
 */

class NiscahyaChatbot {
    constructor(apiUrl = 'http://localhost:8000', sessionId = null) {
        this.apiUrl = apiUrl.replace(/\/$/, ''); // Remove trailing slash
        this.sessionId = sessionId || this.generateSessionId();
    }

    /**
     * Generate unique session ID
     */
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * Send message to chatbot
     * @param {string} message - User message
     * @returns {Promise<Object>} Chat response
     */
    async sendMessage(message) {
        try {
            const response = await fetch(`${this.apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                answer: data.answer,
                intent: data.intent,
                product: data.product,
                sessionId: this.sessionId
            };
        } catch (error) {
            console.error('Chatbot API Error:', error);
            return {
                success: false,
                error: error.message,
                answer: 'Maaf, terjadi kesalahan saat menghubungi server. Silakan coba lagi.',
                sessionId: this.sessionId
            };
        }
    }

    /**
     * Create lead/contact
     * @param {Object} leadData - Lead information
     * @param {string} leadData.name - Customer name
     * @param {string} leadData.whatsapp - WhatsApp number
     * @param {string} leadData.project_needs - Project requirements
     * @returns {Promise<Object>} Lead creation response
     */
    async createLead(leadData) {
        try {
            const response = await fetch(`${this.apiUrl}/api/lead`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(leadData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                lead: data
            };
        } catch (error) {
            console.error('Lead API Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get chat history
     * @param {number} limit - Number of messages to retrieve (default: 50)
     * @returns {Promise<Object>} Chat history
     */
    async getHistory(limit = 50) {
        try {
            const response = await fetch(`${this.apiUrl}/api/history?session_id=${this.sessionId}&limit=${limit}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                history: data
            };
        } catch (error) {
            console.error('History API Error:', error);
            return {
                success: false,
                error: error.message,
                history: []
            };
        }
    }

    /**
     * Clear chat history
     * @returns {Promise<Object>} Clear history response
     */
    async clearHistory() {
        try {
            const response = await fetch(`${this.apiUrl}/api/history?session_id=${this.sessionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                message: data.message
            };
        } catch (error) {
            console.error('Clear History API Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Upload knowledge base documents
     * @param {FileList|Array} files - Files to upload
     * @returns {Promise<Object>} Upload response
     */
    async uploadDocuments(files) {
        try {
            const formData = new FormData();

            // Handle both FileList and Array
            const fileArray = Array.from(files);
            fileArray.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch(`${this.apiUrl}/api/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                upload: data
            };
        } catch (error) {
            console.error('Upload API Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get API health status
     * @returns {Promise<Object>} API status
     */
    async getStatus() {
        try {
            const response = await fetch(`${this.apiUrl}/`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return {
                success: true,
                status: data
            };
        } catch (error) {
            console.error('Status API Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NiscahyaChatbot;
} else if (typeof define === 'function' && define.amd) {
    define([], function() { return NiscahyaChatbot; });
} else if (typeof window !== 'undefined') {
    window.NiscahyaChatbot = NiscahyaChatbot;
}