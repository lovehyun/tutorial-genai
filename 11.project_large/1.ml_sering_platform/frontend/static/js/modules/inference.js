import { api } from './api.js';
import { showToast } from './toast.js';

export const inference = {
    async loadModelInfo(modelId) {
        try {
            const model = await api.get(`/models/${modelId}`);
            this.renderModelInfo(model);
            this.createInputForm(model);
        } catch (error) {
            showToast('Failed to load model information', 'error');
        }
    },

    renderModelInfo(model) {
        const container = document.getElementById('modelInfo');
        container.innerHTML = `
            <div class="bg-gray-50 p-4 rounded-md">
                <h3 class="text-lg font-medium text-gray-900">${model.name}</h3>
                <p class="text-sm text-gray-500">${model.description || 'No description'}</p>
                <p class="text-xs text-gray-400 mt-1">
                    Type: ${model.model_type} | Framework: ${model.framework} | Created: ${new Date(model.created_at).toLocaleString()}
                </p>
            </div>
        `;
    },

    createInputForm(model) {
        const container = document.getElementById('inputForm');
        let formHtml = '';

        switch (model.model_type) {
            case 'classification':
                formHtml = this.createClassificationForm();
                break;
            case 'regression':
                formHtml = this.createRegressionForm();
                break;
            case 'object_detection':
                formHtml = this.createObjectDetectionForm();
                break;
            case 'text_generation':
                formHtml = this.createTextGenerationForm();
                break;
            default:
                formHtml = '<p class="text-red-500">Unsupported model type</p>';
        }

        container.innerHTML = formHtml;
        this.attachFormSubmitHandler(model.id);
    },

    createClassificationForm() {
        return `
            <form id="inferenceForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Input Text</label>
                    <textarea name="input" rows="4" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"></textarea>
                </div>
                <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
                    Predict
                </button>
            </form>
        `;
    },

    createRegressionForm() {
        return `
            <form id="inferenceForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Input Features</label>
                    <textarea name="input" rows="4" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        placeholder="Enter features as JSON array"></textarea>
                </div>
                <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
                    Predict
                </button>
            </form>
        `;
    },

    createObjectDetectionForm() {
        return `
            <form id="inferenceForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Upload Image</label>
                    <input type="file" name="input" accept="image/*" required
                        class="mt-1 block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-indigo-50 file:text-indigo-700
                        hover:file:bg-indigo-100">
                </div>
                <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
                    Detect Objects
                </button>
            </form>
        `;
    },

    createTextGenerationForm() {
        return `
            <form id="inferenceForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700">Prompt</label>
                    <textarea name="input" rows="4" required
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        placeholder="Enter your prompt here"></textarea>
                </div>
                <button type="submit" class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
                    Generate
                </button>
            </form>
        `;
    },

    attachFormSubmitHandler(modelId) {
        const form = document.getElementById('inferenceForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                const result = await this.runInference(modelId, formData);
                this.displayResult(result);
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    },

    async runInference(modelId, formData) {
        const response = await fetch(`http://127.0.0.1:5000/api/v1/models/${modelId}/inference`, {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Inference failed');
        }

        return await response.json();
    },

    displayResult(result) {
        const container = document.getElementById('result');
        container.innerHTML = `
            <pre class="whitespace-pre-wrap">${JSON.stringify(result, null, 2)}</pre>
        `;
    }
};

// 전역 스코프에 inference 객체 추가
window.inference = inference; 