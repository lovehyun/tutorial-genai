const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// 정적 파일 제공
app.use(express.static(path.join(__dirname, 'public')));

// 사용자 목록 저장
const userMap = {};

// 루트 접속 시 index.html 제공
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 소켓 연결 처리
io.on('connection', (socket) => {
    console.log(`✅ 사용자 연결: ${socket.id}`);

    // 사용자 등록
    socket.on('user joined', (username) => {
        userMap[socket.id] = username;
        console.log(`👤 등록: ${username}`);
    });

    // 메시지 수신 및 전체 전송
    socket.on('chat message', (data) => {
        console.log(`📨 ${data.username}: ${data.message}`);
        io.emit('chat message', data); // 모든 클라이언트에 전송
    });

    // 연결 해제
    socket.on('disconnect', () => {
        const username = userMap[socket.id];
        if (username) {
            console.log(`❌ 연결 종료: ${username}`);
            delete userMap[socket.id];
        }
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`서버 실행 중: http://localhost:${PORT}`);
});
