const socket = io();
let username = '';

const usernameInput = document.getElementById('usernameInput');
const messageInput = document.getElementById('messageInput');
const messages = document.getElementById('messages');

usernameInput.addEventListener('change', () => {
    username = usernameInput.value.trim();
    if (username) {
        socket.emit('user joined', username);
    }
});

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const message = messageInput.value.trim();
    if (!username) return alert('이름을 입력해주세요.');
    if (!message) return;

    const data = { username, message };
    socket.emit('chat message', data);
    appendMessage(`나: ${message}`, 'myMessage');
    messageInput.value = '';
}

socket.on('chat message', ({ username: sender, message }) => {
    if (sender !== username) {
        appendMessage(`${sender}: ${message}`, 'otherMessage');
    }
});

function appendMessage(text, className) {
    const div = document.createElement('div');
    div.className = className; // 'myMessage' 또는 'otherMessage'

    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;

    div.appendChild(bubble);
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}
