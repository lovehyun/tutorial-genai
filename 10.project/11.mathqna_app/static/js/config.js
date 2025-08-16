// static/js/config.js
// 클라이언트 사이드 설정 파일

window.APP_CONFIG = {
    // API 설정
    API: {
        BASE_URL: '/api',
        TIMEOUT: 30000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 1000
    },
    
    // UI 설정
    UI: {
        ANIMATION_DURATION: 300,
        STATUS_CHECK_INTERVAL: 30000,
        AUTO_SAVE_INTERVAL: 2000,
        MESSAGE_DURATION: 5000,
        LOADING_MIN_DURATION: 500
    },
    
    // 저장소 키
    STORAGE_KEYS: {
        ANSWER_PREFIX: 'problem_',
        USER_PREFERENCES: 'user_preferences',
        THEME: 'theme_preference',
        LAST_PROBLEM: 'last_problem_id'
    },
    
    // 테마 설정
    THEMES: {
        LIGHT: 'light',
        DARK: 'dark',
        AUTO: 'auto'
    },
    
    // 메시지 타입
    MESSAGE_TYPES: {
        SUCCESS: 'success',
        ERROR: 'danger',
        WARNING: 'warning',
        INFO: 'info'
    },
    
    // 키보드 단축키
    SHORTCUTS: {
        SUBMIT: 'Enter',
        HINT: 'h',
        SOLUTION: 's',
        RESET: 'r',
        HELP: '/',
        TOGGLE_THEME: 't'
    },
    
    // 점수 범위
    SCORE_RANGES: {
        EXCELLENT: 90,
        GOOD: 75,
        AVERAGE: 60
    },
    
    // 개발 모드 설정
    DEV: {
        CONSOLE_LOGS: true,
        PERFORMANCE_MONITORING: true,
        ERROR_REPORTING: true
    }
};

// 환경별 설정 오버라이드
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    // 개발 환경
    window.APP_CONFIG.DEV.CONSOLE_LOGS = true;
    window.APP_CONFIG.API.TIMEOUT = 60000; // 개발시 더 긴 타임아웃
} else {
    // 프로덕션 환경
    window.APP_CONFIG.DEV.CONSOLE_LOGS = false;
    window.APP_CONFIG.UI.STATUS_CHECK_INTERVAL = 60000; // 더 긴 간격
}
