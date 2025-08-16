// static/js/main.js
// 메인 JavaScript 파일 - 전역 함수 및 공통 기능

'use strict';

// 전역 설정
const CONFIG = {
    API_BASE_URL: '/api',
    STATUS_CHECK_INTERVAL: 30000, // 30초
    AUTO_SAVE_INTERVAL: 2000,     // 2초
    ANIMATION_DURATION: 300,
    MAX_RETRIES: 3
};

// 전역 상태 관리
const AppState = {
    isLoading: false,
    serviceStatus: 'unknown',
    retryCount: 0,
    currentProblemId: null
};

// 유틸리티 함수들
const Utils = {
    // API 호출 래퍼
    async apiCall(endpoint, options = {}) {
        const url = `${CONFIG.API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API call failed: ${endpoint}`, error);
            throw error;
        }
    },

    // 로딩 상태 관리
    showLoading(message = 'AI가 작업 중입니다...') {
        if (AppState.isLoading) return;
        
        AppState.isLoading = true;
        const loadingHtml = `
            <div class="loading-overlay" id="loadingOverlay">
                <div class="loading-content">
                    <div class="spinner-custom"></div>
                    <p class="mt-3">${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    },

    hideLoading() {
        AppState.isLoading = false;
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => loadingOverlay.remove(), 300);
        }
    },

    // 메시지 표시
    showMessage(message, type = 'info', duration = 5000) {
        const messageId = 'message-' + Date.now();
        const messageHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" id="${messageId}" role="alert">
                <i class="fas fa-${this.getIconForType(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertAdjacentHTML('afterbegin', messageHtml);
        }
        
        // 자동 제거
        if (duration > 0) {
            setTimeout(() => {
                const messageElement = document.getElementById(messageId);
                if (messageElement) {
                    messageElement.remove();
                }
            }, duration);
        }
    },

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    // 점수에 따른 CSS 클래스 반환
    getScoreClass(score) {
        if (score >= 90) return 'score-excellent';
        if (score >= 75) return 'score-good';
        if (score >= 60) return 'score-average';
        return 'score-poor';
    },

    // 로컬 스토리지 관리
    saveToStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
        }
    },

    loadFromStorage(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn('Failed to load from localStorage:', error);
            return defaultValue;
        }
    },

    // 디바운스 함수
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 요소 애니메이션
    animateElement(element, animationClass, duration = CONFIG.ANIMATION_DURATION) {
        return new Promise((resolve) => {
            element.classList.add(animationClass);
            setTimeout(() => {
                element.classList.remove(animationClass);
                resolve();
            }, duration);
        });
    }
};

// 서비스 상태 관리
const ServiceStatus = {
    async check() {
        try {
            const data = await Utils.apiCall('/status');
            this.update(data.status, data.message);
            AppState.retryCount = 0;
            return data;
        } catch (error) {
            console.error('Service status check failed:', error);
            AppState.retryCount++;
            
            if (AppState.retryCount < CONFIG.MAX_RETRIES) {
                setTimeout(() => this.check(), 5000); // 5초 후 재시도
            } else {
                this.update('error', '서비스 상태를 확인할 수 없습니다.');
            }
            throw error;
        }
    },

    update(status, message = '') {
        AppState.serviceStatus = status;
        const statusElement = document.getElementById('serviceStatus');
        
        if (!statusElement) return;

        const statusConfig = {
            'available': {
                class: 'badge bg-success',
                indicator: 'status-available',
                text: 'AI 서비스 정상',
                icon: 'check-circle'
            },
            'unavailable': {
                class: 'badge bg-danger',
                indicator: 'status-unavailable',
                text: 'AI 서비스 오류',
                icon: 'exclamation-triangle'
            },
            'error': {
                class: 'badge bg-warning',
                indicator: 'status-unavailable',
                text: '상태 불명',
                icon: 'question-circle'
            }
        };

        const config = statusConfig[status] || statusConfig['error'];
        
        statusElement.className = config.class;
        statusElement.innerHTML = `
            <span class="status-indicator ${config.indicator}"></span>
            <i class="fas fa-${config.icon} me-1"></i>
            ${config.text}
        `;

        // 버튼 상태 업데이트
        this.updateButtonStates(status === 'available');
    },

    updateButtonStates(isAvailable) {
        const buttons = document.querySelectorAll('[data-requires-service="true"]');
        buttons.forEach(button => {
            button.disabled = !isAvailable;
            if (!isAvailable) {
                button.title = 'AI 서비스를 사용할 수 없습니다.';
            } else {
                button.removeAttribute('title');
            }
        });
    },

    startPeriodicCheck() {
        this.check(); // 즉시 확인
        setInterval(() => this.check(), CONFIG.STATUS_CHECK_INTERVAL);
    }
};

// 자동 저장 기능
const AutoSave = {
    timers: new Map(),

    enable(elementId, storageKey, interval = CONFIG.AUTO_SAVE_INTERVAL) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // 기존 타이머 정리
        this.disable(elementId);

        // 저장된 값 복원
        const savedValue = Utils.loadFromStorage(storageKey);
        if (savedValue && !element.value.trim()) {
            element.value = savedValue;
        }

        // 자동 저장 설정
        const debouncedSave = Utils.debounce((value) => {
            Utils.saveToStorage(storageKey, value);
        }, interval);

        const handleInput = () => debouncedSave(element.value);
        element.addEventListener('input', handleInput);

        this.timers.set(elementId, { element, handleInput, storageKey });
    },

    disable(elementId) {
        const timer = this.timers.get(elementId);
        if (timer) {
            timer.element.removeEventListener('input', timer.handleInput);
            this.timers.delete(elementId);
        }
    },

    clear(storageKey) {
        localStorage.removeItem(storageKey);
    }
};

// MathJax 관리
const MathRenderer = {
    isReady: false,

    init() {
        if (window.MathJax) {
            // MathJax 3.x에서는 startup.promise를 사용
            if (window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise.then(() => {
                    this.isReady = true;
                    console.log('MathJax ready');
                }).catch(error => {
                    console.warn('MathJax initialization failed:', error);
                });
            } else {
                // MathJax가 이미 로드된 경우
                this.isReady = true;
                console.log('MathJax already ready');
            }
        }
    },

    async render(element) {
        if (!this.isReady || !window.MathJax) {
            console.warn('MathJax not ready');
            return;
        }

        try {
            // MathJax 3.x에서는 typesetPromise 대신 typeset을 사용
            if (window.MathJax.typesetPromise) {
                await window.MathJax.typesetPromise([element]);
            } else if (window.MathJax.typeset) {
                await window.MathJax.typeset([element]);
            } else {
                console.warn('MathJax typeset method not available');
            }
        } catch (error) {
            console.warn('MathJax rendering failed:', error);
        }
    },

    async renderAll() {
        if (!this.isReady || !window.MathJax) {
            console.warn('MathJax not ready');
            return;
        }

        try {
            // MathJax 3.x에서는 typesetPromise 대신 typeset을 사용
            if (window.MathJax.typesetPromise) {
                await window.MathJax.typesetPromise();
            } else if (window.MathJax.typeset) {
                await window.MathJax.typeset();
            } else {
                console.warn('MathJax typeset method not available');
            }
        } catch (error) {
            console.warn('MathJax rendering failed:', error);
        }
    }
};

// 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('Math Q&A System initialized');
    
    // utils.js 로드 후 KeyboardShortcuts 추가
    if (window.MathQAUtils?.KeyboardShortcuts) {
        window.MathQA.KeyboardShortcuts = window.MathQAUtils.KeyboardShortcuts;
    }
    
    // 서비스 상태 확인 시작
    ServiceStatus.startPeriodicCheck();
    
    // MathJax 초기화
    MathRenderer.init();
    
    // ThemeManager 초기화 (window.MathQA가 준비된 후)
    if (window.MathQAUtils?.ThemeManager) {
        window.MathQAUtils.ThemeManager.init();
    }
    
    // 홈페이지 기능 초기화 (홈페이지인 경우)
    if (document.querySelector('.hero-section')) {
        if (window.MathQAUtils?.HomePage) {
            window.MathQAUtils.HomePage.init();
        }
    }
    
    // 전역 오류 처리
    window.addEventListener('unhandledrejection', (event) => {
        console.error('Unhandled promise rejection:', event.reason);
        Utils.showMessage('예상치 못한 오류가 발생했습니다.', 'danger');
    });
});

// 전역 객체로 내보내기
window.MathQA = {
    Utils,
    ServiceStatus,
    AutoSave,
    MathRenderer,
    AppState,
    CONFIG
};
