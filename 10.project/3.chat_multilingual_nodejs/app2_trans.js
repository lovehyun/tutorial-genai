// server.js - 최소 기능 구현
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const OpenAI = require('openai');
const dotenv = require('dotenv');

// 환경변수 로드
dotenv.config();

// Express 앱 초기화
const app = express();
const server = http.createServer(app);

// Socket.IO 설정
const io = new Server(server);

// 정적 파일 제공
app.use(express.static(path.join(__dirname, 'public')));

// OpenAI 클라이언트 초기화
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

// 사용자 정보 저장
const userMap = {}; // 소켓 ID -> 사용자 정보

// 메시지를 번역하는 함수
async function translateMessage(text, targetLang) {
    try {
        // 언어코드를 명확한 언어명으로 매핑
        const languageMap = {
            ko: 'Korean',
            en: 'English',
            ja: 'Japanese',
            zh: 'Chinese',
            es: 'Spanish',
            fr: 'French',
        };

        // 언어 코드를 전체 언어명으로 변환
        const fullLanguageName = languageMap[targetLang] || targetLang;

        console.log(`번역 시작: ${targetLang} (${fullLanguageName})`);

        const response = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: [
                {
                    role: 'system',
                    content: `You are a translator. Translate the following text to ${fullLanguageName}. Only provide the translation, nothing else.`,
                },
                { role: 'user', content: text },
            ],
        });

        const translated = response.choices[0].message.content;
        console.log(`번역 완료: "${text}" -> "${translated}"`);
        return translated;
    } catch (error) {
        console.error(`번역 오류: ${error}`);
        return text; // 오류 발생 시 원문 반환
    }
}

// 루트 페이지 요청 시 index.html 제공
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index2.html'));
});

// Socket.IO 이벤트 처리
io.on('connection', (socket) => {
    console.log(`✅ 새 사용자 연결: ${socket.id}`);

    // 새로운 사용자가 참여했을 때
    socket.on('user joined', (username) => {
        // 기본 언어는 한국어로 설정
        userMap[socket.id] = { username, language: 'ko' };
        console.log(`👤 사용자 등록: ${username} (${socket.id})`);

        // 사용자에게 초기 상태 전송
        socket.emit('initialization', {
            currentLanguage: 'ko',
        });
    });

    // 사용자가 언어를 변경했을 때
    socket.on('set language', (lang) => {
        if (userMap[socket.id]) {
            userMap[socket.id].language = lang;
            console.log(`🌍 언어 설정: ${userMap[socket.id].username} -> ${lang}`);

            // 언어 변경 확인
            socket.emit('language updated', {
                language: lang,
            });
        }
    });

    // 채팅 메시지를 수신했을 때
    socket.on('chat message', async (data) => {
        console.log(`📨 메시지 수신: ${data.username} -> "${data.message}"`);

        // 다른 사용자에게 번역된 메시지 전송
        for (const sid in userMap) {
            if (sid !== socket.id) {
                const targetLang = userMap[sid].language;
                const translatedMsg = await translateMessage(data.message, targetLang);

                io.to(sid).emit('chat message', {
                    username: data.username,
                    message: translatedMsg,
                    timestamp: data.timestamp,
                });
            }
        }
    });

    // 클라이언트가 연결 해제됐을 때
    socket.on('disconnect', () => {
        if (userMap[socket.id]) {
            console.log(`❌ 사용자 연결 종료: ${userMap[socket.id].username} (${socket.id})`);
            delete userMap[socket.id];
        } else {
            console.log(`❌ 알 수 없는 사용자 연결 종료: ${socket.id}`);
        }
    });
});

// 서버 실행
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`서버가 포트 ${PORT}에서 실행 중입니다`);
});
