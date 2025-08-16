/**
 * 입력 관리 모듈
 */
class InputManager {
    constructor(socketManager, chatManager) {
        this.socketManager = socketManager;
        this.chatManager = chatManager;
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.setupEventListeners();
    }

    /**
     * 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 전송 버튼 클릭
        this.sendButton.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enter 키 입력
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 입력 필드 자동 높이 조정
        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
        });

        // 입력 필드 포커스 시 자동 높이 조정
        this.messageInput.addEventListener('focus', () => {
            this.adjustTextareaHeight();
        });
    }

    /**
     * 메시지 전송
     */
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // 사용자 메시지 추가
        this.chatManager.addUserMessage(message);
        
        // 입력 필드 초기화
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        
        // 처리 중 표시
        this.chatManager.showProcessingIndicator();
        
        // 소켓으로 메시지 전송
        this.socketManager.sendMessage(message);
    }

    /**
     * 텍스트 영역 높이 자동 조정
     */
    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    /**
     * 입력 필드 비활성화/활성화
     */
    setInputDisabled(disabled) {
        this.messageInput.disabled = disabled;
        this.sendButton.disabled = disabled;
    }

    /**
     * 입력 필드 포커스
     */
    focusInput() {
        this.messageInput.focus();
    }

    /**
     * 입력 필드 값 가져오기
     */
    getInputValue() {
        return this.messageInput.value.trim();
    }

    /**
     * 입력 필드 값 설정
     */
    setInputValue(value) {
        this.messageInput.value = value;
        this.adjustTextareaHeight();
    }
}
