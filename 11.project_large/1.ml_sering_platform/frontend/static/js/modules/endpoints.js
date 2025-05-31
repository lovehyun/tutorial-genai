import { api } from './api.js';
import { showToast } from './toast.js';

export const endpoints = {
    async loadEndpoints() {
        try {
            const endpointList = await api.get('/endpoints');
            const container = document.getElementById('endpointsList');
            
            if (endpointList.length === 0) {
                container.innerHTML = `
                    <div class="p-4 text-center text-gray-500">
                        No endpoints found. Create your first endpoint to get started.
                    </div>
                `;
                return;
            }

            container.innerHTML = endpointList.map(endpoint => `
                <div class="p-4 border-b last:border-b-0">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="text-lg font-medium text-gray-900">${endpoint.name}</h3>
                            <p class="text-sm text-gray-500">${endpoint.description || 'No description'}</p>
                            <p class="text-xs text-gray-400 mt-1">
                                Model: ${endpoint.model_name} | Framework: ${endpoint.framework} | Created: ${new Date(endpoint.created_at).toLocaleString()}
                            </p>
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="endpoints.testEndpoint(${endpoint.id})" 
                                class="text-indigo-600 hover:text-indigo-800">
                                Test
                            </button>
                            <button onclick="endpoints.deleteEndpoint(${endpoint.id})"
                                class="text-red-600 hover:text-red-800">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            showToast('Failed to load endpoints', 'error');
        }
    },

    async createEndpoint(data) {
        try {
            const response = await api.post('/endpoints', data);
            await this.loadEndpoints();
            return response;
        } catch (error) {
            throw new Error('Failed to create endpoint');
        }
    },

    async deleteEndpoint(id) {
        if (!confirm('Are you sure you want to delete this endpoint?')) {
            return;
        }
        
        try {
            await api.delete(`/endpoints/${id}`);
            await this.loadEndpoints();
            showToast('Endpoint deleted successfully', 'success');
        } catch (error) {
            showToast('Failed to delete endpoint', 'error');
        }
    },

    testEndpoint(id) {
        window.location.href = `/inference.html?endpoint_id=${id}`;
    }
};

// 전역 스코프에 endpoints 객체 추가
window.endpoints = endpoints; 