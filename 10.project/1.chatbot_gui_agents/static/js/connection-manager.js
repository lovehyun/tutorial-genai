/**
 * 연결 상태 관리 모듈
 */
class ConnectionManager {
    constructor() {
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
    }

    /**
     * 연결 상태 업데이트
     */
    updateConnectionStatus(connected) {
        if (connected) {
            this.statusIndicator.classList.add('connected');
            this.statusText.textContent = '연결됨';
        } else {
            this.statusIndicator.classList.remove('connected');
            this.statusText.textContent = '연결 해제됨';
        }
    }

    /**
     * 연결 상태 확인
     */
    isConnected() {
        return this.statusIndicator.classList.contains('connected');
    }

    /**
     * 상태 텍스트 업데이트
     */
    updateStatusText(text) {
        this.statusText.textContent = text;
    }

    /**
     * 연결 상태 초기화
     */
    reset() {
        this.statusIndicator.classList.remove('connected');
        this.statusText.textContent = '연결 중...';
    }
}
