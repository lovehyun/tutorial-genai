// static/script.js
// 소켓 연결 생성
const socket = io();

// 사용자 이름 변수 초기화
let username = '';

// DOM 요소 참조
const usernameInput = document.getElementById('usernameInput');
const messageInput = document.getElementById('messageInput');
const languageSelect = document.getElementById('languageSelect');
const messages = document.getElementById('messages');
const typingIndicator = document.getElementById('typingIndicator');

// 소켓 서버에 연결되었을 때 로그 출력
socket.on('connect', () => {
    console.log(`🔗 연결 완료: ${socket.id}`);
});

// 사용자 이름 입력 시 서버에 'user joined' 이벤트 전송
usernameInput.addEventListener('change', () => {
    username = usernameInput.value;
    if (username.trim()) {
        socket.emit('user joined', username);
        console.log(`사용자 이름 설정: ${username}`);
    }
});

// 언어 선택 변경 시 서버에 'set language' 이벤트 전송
languageSelect.addEventListener('change', () => {
    const selectedLanguage = languageSelect.value;
    socket.emit('set language', selectedLanguage);
    console.log(`언어 변경: ${selectedLanguage}`);
});

// 초기화 데이터 수신
socket.on('initialization', (data) => {
    console.log('초기화 데이터 수신:', data);
    if (data.currentLanguage) {
        languageSelect.value = data.currentLanguage;
    }
});

// 언어 설정 업데이트 확인
socket.on('language updated', (data) => {
    console.log(`언어가 변경되었습니다: ${data.language}`);
});

// Enter 키 입력 시 메시지 전송
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// 메시지 전송 함수
function sendMessage() {
    const message = messageInput.value.trim();

    if (!username) {
        alert('먼저 이름을 입력해주세요.');
        return;
    }

    if (message) {
        const timestamp = Date.now();

        // 내 화면에 바로 메시지 표시
        appendMessage(message, 'myMessage', timestamp);

        // 서버에 메시지 전송
        socket.emit('chat message', {
            username,
            message,
            timestamp,
        });

        // 입력창 초기화
        messageInput.value = '';

        // 스크롤 하단으로 이동
        scrollToBottom();
    }
}

// 서버로부터 채팅 메시지를 받았을 때
socket.on('chat message', ({ username: sender, message, timestamp }) => {
    // 다른 사용자의 메시지만 표시 (내 메시지는 이미 표시했음)
    if (sender !== username) {
        appendMessage(`${sender}: ${message}`, 'otherMessage', timestamp);
        scrollToBottom();
    }
});

// 메시지를 화면에 추가
function appendMessage(message, className, timestamp) {
    const li = document.createElement('li');
    li.className = className;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';

    // myMessage일 경우 '나: '라는 접두사를 제거 (이미 오른쪽 정렬됨)
    if (className === 'myMessage') {
        bubble.textContent = message.startsWith('나: ') ? message.substring(3) : message;
    } else {
        bubble.textContent = message;
    }

    li.appendChild(bubble);
    messages.appendChild(li);
}

// 스크롤을 메시지 하단으로 이동
function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}
