/**
 * 메인 애플리케이션 모듈
 */
class ChatApp {
    constructor() {
        this.initializeModules();
        this.setupEventHandlers();
    }

    /**
     * 모듈들 초기화
     */
    initializeModules() {
        // Socket.IO 연결 관리
        this.socketManager = new SocketManager();
        
        // 연결 상태 관리
        this.connectionManager = new ConnectionManager();
        
        // Agent 상태 관리
        this.agentManager = new AgentManager();
        
        // 채팅 메시지 관리
        this.chatManager = new ChatManager();
        
        // 입력 관리
        this.inputManager = new InputManager(this.socketManager, this.chatManager);
    }

    /**
     * 이벤트 핸들러 설정
     */
    setupEventHandlers() {
        // 연결 상태 이벤트
        this.socketManager.on('connection', (data) => {
            this.connectionManager.updateConnectionStatus(data.connected);
        });

        // Agent 상태 업데이트 이벤트
        this.socketManager.on('agent_status', (data) => {
            this.agentManager.updateAgentStatus(data);
            
            // 전체 처리 상태 업데이트
            if (data.status === 'processing') {
                this.chatManager.updateProcessingStatus(data.message);
            } else if (data.status === 'complete') {
                this.chatManager.updateProcessingStatus('처리 완료');
            }
        });

        // 채팅 응답 수신 이벤트
        this.socketManager.on('chat_response', (data) => {
            this.chatManager.addAssistantMessage(data);
            this.chatManager.hideProcessingIndicator();
        });

        // 오류 처리 이벤트
        this.socketManager.on('error', (data) => {
            this.chatManager.addErrorMessage(data.message);
            this.chatManager.hideProcessingIndicator();
        });
    }

    /**
     * 애플리케이션 시작
     */
    start() {
        console.log('AI Agent Chatbot 애플리케이션이 시작되었습니다.');
        
        // 초기 포커스를 입력 필드로 설정
        this.inputManager.focusInput();
    }

    /**
     * 애플리케이션 정리
     */
    cleanup() {
        // 필요한 정리 작업 수행
        console.log('애플리케이션이 정리되었습니다.');
    }
}

// DOM이 로드된 후 애플리케이션 시작
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    window.chatApp.start();
});

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', () => {
    if (window.chatApp) {
        window.chatApp.cleanup();
    }
});
