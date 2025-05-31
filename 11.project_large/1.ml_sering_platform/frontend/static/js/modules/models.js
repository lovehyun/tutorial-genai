import { api } from './api.js';
import { showToast } from './toast.js';

export const models = {
    async loadModels() {
        try {
            const modelList = await api.get('/models');
            const container = document.getElementById('modelsList');
            
            if (modelList.length === 0) {
                container.innerHTML = `
                    <div class="p-4 text-center text-gray-500">
                        No models found. Upload your first model to get started.
                    </div>
                `;
                return;
            }

            container.innerHTML = modelList.map(model => `
                <div class="p-4 border-b last:border-b-0">
                    <div class="flex justify-between items-start">
                        <div>
                            <h3 class="text-lg font-medium text-gray-900">${model.name}</h3>
                            <p class="text-sm text-gray-500">${model.description || 'No description'}</p>
                            <p class="text-xs text-gray-400 mt-1">
                                Type: ${model.model_type} | Framework: ${model.framework} | Created: ${new Date(model.created_at).toLocaleString()}
                            </p>
                        </div>
                        <div class="flex space-x-2">
                            <button onclick="models.testModel(${model.id})" 
                                class="text-indigo-600 hover:text-indigo-800">
                                Test
                            </button>
                            <button onclick="models.deleteModel(${model.id})"
                                class="text-red-600 hover:text-red-800">
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            showToast('Failed to load models', 'error');
        }
    },

    async uploadModel(formData) {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/v1/models', {
                method: 'POST',
                body: formData,
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to upload model');
            }

            await this.loadModels();
            return await response.json();
        } catch (error) {
            throw new Error('Failed to upload model');
        }
    },

    async deleteModel(id) {
        if (!confirm('Are you sure you want to delete this model?')) {
            return;
        }
        
        try {
            await api.delete(`/models/${id}`);
            await this.loadModels();
            showToast('Model deleted successfully', 'success');
        } catch (error) {
            showToast('Failed to delete model', 'error');
        }
    },

    testModel(id) {
        window.location.href = `/inference.html?model_id=${id}`;
    }
};

// 전역 스코프에 models 객체 추가
window.models = models; 