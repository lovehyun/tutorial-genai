import { api } from './api.js';
import { showToast } from './toast.js';

export const apiKeys = {
    async loadApiKeys() {
        try {
            const keys = await api.get('/api-keys');
            const container = document.getElementById('apiKeysList');
            
            if (keys.length === 0) {
                container.innerHTML = `
                    <div class="p-4 text-center text-gray-500">
                        No API keys found. Create your first API key to get started.
                    </div>
                `;
                return;
            }

            container.innerHTML = keys.map(key => `
                <div class="p-4 border-b last:border-b-0">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="text-lg font-medium text-gray-900">${key.name}</h3>
                            <p class="text-sm text-gray-500">${key.description || 'No description'}</p>
                            <p class="text-xs text-gray-400 mt-1">Created: ${new Date(key.created_at).toLocaleString()}</p>
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="apiKeys.copyKey('${key.key}')" 
                                class="text-indigo-600 hover:text-indigo-800">
                                Copy Key
                            </button>
                            <button onclick="apiKeys.deleteKey(${key.id})"
                                class="text-red-600 hover:text-red-800">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            showToast('Failed to load API keys', 'error');
        }
    },

    async createApiKey(data) {
        try {
            const response = await api.post('/api-keys', data);
            await this.loadApiKeys();
            return response;
        } catch (error) {
            throw new Error('Failed to create API key');
        }
    },

    async deleteKey(id) {
        if (!confirm('Are you sure you want to delete this API key?')) {
            return;
        }
        
        try {
            await api.delete(`/api-keys/${id}`);
            await this.loadApiKeys();
            showToast('API Key deleted successfully', 'success');
        } catch (error) {
            showToast('Failed to delete API key', 'error');
        }
    },

    copyKey(key) {
        navigator.clipboard.writeText(key);
        showToast('API Key copied to clipboard', 'success');
    }
};

// 전역 스코프에 apiKeys 객체 추가
window.apiKeys = apiKeys; 