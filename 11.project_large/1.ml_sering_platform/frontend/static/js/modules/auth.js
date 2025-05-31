import { API } from './api.js';
import { showToast } from './toast.js';  // 토스트 메시지 모듈 추가

export class Auth {
    constructor() {
        this.api = new API();
    }

    // 토큰 저장
    setToken(token) {
        if (token) {
            localStorage.setItem('token', token);
        }
    }

    // 토큰 가져오기
    getToken() {
        return localStorage.getItem('token');
    }

    // 토큰 삭제
    removeToken() {
        localStorage.removeItem('token');
    }

    // 인증 상태 확인
    isAuthenticated() {
        return !!this.getToken();
    }

    // 로그인
    async login(username, password) {
        try {
            const response = await this.api.login({ username, password });
            if (response.access_token) {
                this.setToken(response.access_token);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    }

    // 로그아웃
    logout() {
        this.removeToken();
        window.location.href = '/login.html';
    }

    async register(email, username, password) {
        try {
            const response = await this.api.register({ email, username, password });
            showToast('Registration completed! Please login.', 'success');
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 1500);
            return response;
        } catch (error) {
            console.error('Registration error:', error);
            showToast(error.message || 'Registration failed.', 'error');
            throw error;
        }
    }
}

// 기본 인스턴스 export
export const auth = new Auth(); 