import { showToast } from './toast.js';

export class API {
    constructor() {
        this.baseUrl = '';  // baseUrl을 빈 문자열로 변경
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // 토큰이 있으면 Authorization 헤더에 추가
        const token = localStorage.getItem('token');
        console.log('Current token in request:', token);  // 디버깅을 위한 로그 추가
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            console.log('Request headers:', headers);  // 디버깅을 위한 로그 추가
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                if (response.status === 401) {
                    console.log('401 Unauthorized response:', await response.text());  // 디버깅을 위한 로그 추가
                    localStorage.removeItem('token');
                    window.location.href = '/login.html';
                }
                throw new Error(response.statusText);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Auth endpoints
    async login(data) {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        const response = await fetch(`/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString()
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        const result = await response.json();
        console.log('Login response:', result);  // 디버깅을 위한 로그 추가
        
        if (result.access_token) {
            localStorage.setItem('token', result.access_token);
            console.log('Token stored:', result.access_token);  // 디버깅을 위한 로그 추가
        } else {
            console.error('No access_token in response:', result);  // 디버깅을 위한 로그 추가
        }
        
        return result;
    }

    async register(data) {
        return this.request('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Model endpoints
    async getModels() {
        return this.request('/api/v1/models', {
            method: 'GET'
        });
    }

    async getModel(id) {
        return this.request(`/api/v1/models/${id}`, {
            method: 'GET'
        });
    }

    async createModel(data) {
        return this.request('/api/v1/models', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async deleteModel(id) {
        return this.request(`/api/v1/models/${id}`, {
            method: 'DELETE'
        });
    }

    // Endpoint endpoints
    async getEndpoints() {
        try {
            const response = await fetch(`/api/v1/endpoints`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.status === 401) {
                window.location.href = '/login.html';
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error fetching endpoints:', error);
            throw error;
        }
    }

    async getEndpoint(id) {
        return this.request(`/api/v1/endpoints/${id}`, {
            method: 'GET'
        });
    }

    async createEndpoint(data) {
        return this.request('/api/v1/endpoints', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async deleteEndpoint(id) {
        return this.request(`/api/v1/endpoints/${id}`, {
            method: 'DELETE'
        });
    }

    // API Key endpoints
    async getApiKeys() {
        return this.request('/api/v1/api-keys', {
            method: 'GET'
        });
    }

    async createApiKey(data) {
        return this.request('/api/v1/api-keys', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async updateApiKey(id, data) {
        return this.request(`/api/v1/api-keys/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async deleteApiKey(id) {
        return this.request(`/api/v1/api-keys/${id}`, {
            method: 'DELETE'
        });
    }

    // Inference endpoints
    async runInference(endpointId, data) {
        return this.request(`/api/v1/endpoints/${endpointId}/inference`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async uploadModel(formData) {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                throw new Error('No authentication token found');
            }

            const response = await fetch(`${this.baseUrl}/api/v1/models`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            console.log('[DEBUG] Upload response status:', response.status);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to upload model');
            }

            return await response.json();
        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }
}

// 기본 인스턴스 export
export const api = new API(); 