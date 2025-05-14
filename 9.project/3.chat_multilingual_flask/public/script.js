// 소켓 연결 생성
const socket = io();

// 사용자 이름, 타이핑 중인 사용자 목록, 총 사용자 수 변수 초기화
let username = '';
let typingUsers = [];
let totalUsers = 0;

// DOM 요소 참조
const usernameInput = document.getElementById('usernameInput');
const messageInput = document.getElementById('messageInput');
const languageSelect = document.getElementById('languageSelect');
const messages = document.getElementById('messages');
const typingIndicator = document.getElementById('typingIndicator');

// 소켓 서버에 연결되었을 때 콘솔에 ID 출력
socket.on('connect', () => {
    console.log(`🔗 Connected with socket ID: ${socket.id}`);
});

// 사용자 이름 입력 시 서버에 'user joined' 이벤트 전송
usernameInput.addEventListener('change', () => {
    username = usernameInput.value;
    socket.emit('user joined', username);
});

// 언어 선택 변경 시 서버에 'set language' 이벤트 전송
languageSelect.addEventListener('change', () => {
    socket.emit('set language', languageSelect.value);
});

// 타이핑 이벤트 처리
let typingTimer;
let isTyping = false;

messageInput.addEventListener('input', () => {
    if (!isTyping) {
        socket.emit('typing'); // 처음 입력 시 'typing' 이벤트 전송
        isTyping = true;
    }
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        socket.emit('stop typing'); // 일정 시간 후 타이핑 중지 이벤트 전송
        isTyping = false;
    }, 2000); // 2초 동안 입력이 없으면 중지로 간주
});

// Enter 키 입력 시 메시지 전송
messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// 메시지 전송 함수
function sendMessage() {
    const message = messageInput.value;
    if (!username) {
        alert('Please enter your name first.');
        return;
    }
    if (message.trim()) {
        const timestamp = Date.now();
        appendMessage(`You: ${message}`, 'myMessage', totalUsers - 1, timestamp); // 본인 메시지 표시
        socket.emit('chat message', {
            username,
            message,
            timestamp,
            language: languageSelect.value,
        });
        messageInput.value = ''; // 입력창 초기화
        scrollToBottom(); // 스크롤 하단 이동
    }
}

// 서버로부터 채팅 메시지를 받았을 때
socket.on('chat message', ({ username: sender, message, timestamp, unreadUsers }) => {
    if (sender !== username) {
        appendMessage(`${sender}: ${message}`, 'otherMessage', unreadUsers.length, timestamp);
        socket.emit('read message', { timestamp }); // 읽음 처리
    }
    scrollToBottom();
});

// 다른 사용자가 타이핑 중일 때
socket.on('typing', (typingUser) => {
    if (!typingUsers.includes(typingUser)) {
        typingUsers.push(typingUser);
    }
    updateTypingIndicator();
});

// 다른 사용자가 타이핑을 멈췄을 때
socket.on('stop typing', (typingUser) => {
    typingUsers = typingUsers.filter((user) => user !== typingUser);
    updateTypingIndicator();
});

// 타이핑 인디케이터 업데이트
function updateTypingIndicator() {
    typingIndicator.textContent = typingUsers.length > 0 ? `${typingUsers.join(', ')} is typing...` : '';
}

// 브라우저 포커스 시 모든 메시지에 대해 읽음 처리 전송
window.addEventListener('focus', () => {
    document.querySelectorAll('.readCount').forEach((element) => {
        const messageTimestamp = element.getAttribute('data-timestamp');
        socket.emit('read message', { timestamp: messageTimestamp });
    });
});

// 서버에서 읽음 수 업데이트 받았을 때
socket.on('update read receipt', ({ timestamp, unreadUsers }) => {
    const readCountElement = document.querySelector(`.readCount[data-timestamp="${timestamp}"]`);
    if (readCountElement) {
        readCountElement.textContent = `${unreadUsers.length} unread`;
    }
});

// 전체 접속 사용자 수 업데이트
socket.on('user count', (count) => {
    totalUsers = count;
});

// 메시지를 화면에 추가
function appendMessage(message, className, unreadCount, timestamp) {
    const li = document.createElement('li');
    li.className = className;

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = message;

    const readCount = document.createElement('span');
    readCount.className = 'readCount';
    readCount.textContent = `${unreadCount} unread`;
    readCount.setAttribute('data-timestamp', timestamp);

    li.appendChild(bubble);
    li.appendChild(readCount);
    messages.appendChild(li);
}

// 스크롤을 메시지 하단으로 이동
function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
}
