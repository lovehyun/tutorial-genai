// server.js
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const OpenAI = require('openai');
const dotenv = require('dotenv');

// 환경변수 로드 (.env 파일에서 OPENAI_API_KEY 등을 불러옴)
dotenv.config();

// Express 앱 초기화
const app = express();
const server = http.createServer(app);

// Socket.IO 설정 (모든 출처 허용)
const io = new Server(server, {
    cors: {
        origin: '*',
    },
});

// 정적 파일 제공 (static 폴더)
app.use(express.static(path.join(__dirname, 'public')));

// OpenAI 클라이언트 초기화
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

// 전역 상태 저장 변수들
const messages = []; // 전체 채팅 메시지 목록
const userMap = {}; // 소켓 ID -> 사용자 정보 매핑
const typingUsers = new Set(); // 현재 타이핑 중인 사용자 집합

// 메시지를 target_lang 언어로 번역하는 함수
async function translateMessage(text, targetLang) {
    try {
        const response = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                { role: 'system', content: `Translate to ${targetLang}:` },
                { role: 'user', content: text },
            ],
        });

        const translated = response.choices[0].message.content;
        console.log(`🔄 Translation: ${text} -> ${translated} (${targetLang})`);
        return translated;
    } catch (error) {
        console.error(`Translation error: ${error}`);
        return text; // 오류 발생 시 원문 반환
    }
}

// 루트 페이지 요청 시 index.html 제공
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index3.html'));
});

// Socket.IO 이벤트 처리
io.on('connection', (socket) => {
    const totalUsers = io.engine.clientsCount;
    console.log(`✅ New user connected! Socket ID: ${socket.id}, Total users: ${totalUsers}`);
    io.emit('user count', totalUsers);

    // 새로운 사용자가 참여했을 때
    socket.on('user joined', (username) => {
        userMap[socket.id] = { username, language: 'ko' };
        console.log(`👤 User joined: ${username} (id: ${socket.id})`);
    });

    // 사용자가 언어를 변경했을 때
    socket.on('set language', (lang) => {
        if (userMap[socket.id]) {
            userMap[socket.id].language = lang;
            console.log(`🌍 Language set for ${userMap[socket.id].username}: ${lang}`);
        }
    });

    // 사용자가 타이핑 중일 때
    socket.on('typing', () => {
        const username = userMap[socket.id]?.username || 'Unknown user';
        console.log(`✍️ ${username} is typing...`);
        typingUsers.add(username);
        // 자신을 제외한 다른 사용자들에게 타이핑 알림 전송
        socket.broadcast.emit('typing', username);
    });

    // 사용자가 타이핑을 멈췄을 때
    socket.on('stop typing', () => {
        const username = userMap[socket.id]?.username || 'Unknown user';
        console.log(`✋ ${username} has stopped typing...`);
        typingUsers.delete(username);
        socket.broadcast.emit('stop typing', username);
    });

    // 채팅 메시지를 수신했을 때
    socket.on('chat message', async (data) => {
        const unreadUsers = Object.keys(userMap).filter((sid) => sid !== socket.id);

        // 메시지 저장
        const messageData = {
            username: data.username,
            message: data.message,
            timestamp: data.timestamp,
            unread_users: unreadUsers,
        };
        messages.push(messageData);

        // 다른 사용자에게 해당 언어로 번역된 메시지 전송
        for (const sid in userMap) {
            if (sid !== socket.id) {
                const targetLang = userMap[sid].language;
                const translatedMsg = await translateMessage(data.message, targetLang);

                io.to(sid).emit('chat message', {
                    username: data.username,
                    message: translatedMsg,
                    timestamp: data.timestamp,
                    unreadUsers: unreadUsers,
                });
            }
        }
    });

    // 메시지 읽음 처리
    socket.on('read message', (data) => {
        const msgIdx = messages.findIndex((m) => m.timestamp === data.timestamp);
        if (msgIdx !== -1) {
            const index = messages[msgIdx].unread_users.indexOf(socket.id);
            if (index !== -1) {
                messages[msgIdx].unread_users.splice(index, 1);
                io.emit('update read receipt', {
                    timestamp: data.timestamp,
                    unreadUsers: messages[msgIdx].unread_users,
                });
            }
        }
    });

    // 클라이언트가 연결 해제됐을 때
    socket.on('disconnect', () => {
        const username = userMap[socket.id]?.username || 'Unknown user';
        console.log(`❌ User disconnected: ${username} (ID: ${socket.id})`);

        if (userMap[socket.id]) {
            delete userMap[socket.id];
        }

        // 해당 사용자를 unread 목록에서도 제거
        for (const msg of messages) {
            const index = msg.unread_users.indexOf(socket.id);
            if (index !== -1) {
                msg.unread_users.splice(index, 1);
            }
        }

        // 접속자 수 갱신
        io.emit('user count', io.engine.clientsCount);
    });
});

// 서버 실행
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
