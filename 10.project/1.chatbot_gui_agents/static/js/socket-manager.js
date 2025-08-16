/**
 * Socket.IO 연결 관리 모듈
 */
class SocketManager {
    constructor() {
        this.socket = io();
        this.eventHandlers = new Map();
        this.setupEventListeners();
    }

    /**
     * 기본 이벤트 리스너 설정
     */
    setupEventListeners() {
        // 연결 상태 이벤트
        this.socket.on('connect', () => {
            this.emit('connection', { connected: true });
        });

        this.socket.on('disconnect', () => {
            this.emit('connection', { connected: false });
        });

        // Agent 상태 업데이트
        this.socket.on('agent_status', (data) => {
            this.emit('agent_status', data);
        });

        // 채팅 응답 수신
        this.socket.on('chat_response', (data) => {
            this.emit('chat_response', data);
        });

        // 오류 처리
        this.socket.on('error', (data) => {
            this.emit('error', data);
        });
    }

    /**
     * 이벤트 리스너 등록
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    /**
     * 이벤트 발생
     */
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                handler(data);
            });
        }
    }

    /**
     * 메시지 전송
     */
    sendMessage(message) {
        this.socket.emit('send_message', { message: message });
    }

    /**
     * 연결 상태 확인
     */
    isConnected() {
        return this.socket.connected;
    }
}
