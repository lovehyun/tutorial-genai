document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('user_input');
    const chatLog = document.getElementById('chatlog');
    const languageSelect = document.getElementById('language_select');

    // 디버깅 정보 로그
    console.log('chat.js 로드됨');
    console.log('현재 URL:', window.location.href);

    // URL에서 필요한 정보 추출
    const pathParts = window.location.pathname.split('/');
    console.log('경로 부분:', pathParts);

    // 인덱스: /grade/1/curriculum/0 => ['', 'grade', '1', 'curriculum', '0']
    const grade = pathParts[2]; // 학년은 pathParts[2]에 있음
    const curriculumTitle = document.querySelector('h2').textContent.split(' - ')[1];

    console.log('추출된 학년:', grade);
    console.log('추출된 커리큘럼 제목:', curriculumTitle);

    chatForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const messageText = userInput.value.trim();
        if (!messageText) return;

        console.log('사용자 입력:', messageText);

        // 사용자 입력 표시
        appendMessage('학생', messageText);

        // 입력 필드 초기화
        userInput.value = '';

        try {
            console.log('API 요청 전송 중...');
            // 서버에 메시지 전송
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    grade,
                    curriculum_title: curriculumTitle,
                    user_input: messageText,
                }),
            });

            console.log('API 응답 상태:', response.status);

            if (!response.ok) {
                throw new Error(`서버 응답 오류: ${response.status}`);
            }

            const data = await response.json();
            console.log('API 응답 데이터:', data);

            // 응답 표시
            appendMessage('ChatGPT', data.response);

            // TTS 기능 처리
            handleTextToSpeech(data.response);
        } catch (error) {
            console.error('채팅 요청 중 오류 발생:', error);
            appendMessage('System', '요청 처리 중 오류가 발생했습니다. 다시 시도해주세요.');
        }
    });

    // 메시지를 채팅 로그에 추가하는 함수
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatLog.appendChild(messageElement);

        // 자동 스크롤
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // TTS(음성 합성) 처리 함수
    function handleTextToSpeech(text) {
        const selectedLanguage = languageSelect.value;
        console.log('선택된 TTS 언어:', selectedLanguage);

        if (selectedLanguage !== 'none') {
            const utterance = new SpeechSynthesisUtterance(text);

            if (selectedLanguage === 'en-US') {
                utterance.lang = 'en-US';
            } else if (selectedLanguage === 'ko-KR') {
                utterance.lang = 'ko-KR';
            } else if (selectedLanguage === 'auto') {
                // 간단한 한국어 감지 (한글 포함 여부로 판단)
                const isKorean = /[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/.test(text);
                utterance.lang = isKorean ? 'ko-KR' : 'en-US';
            }

            window.speechSynthesis.speak(utterance);
        }
    }

    // 초기 메시지 (선택 사항)
    appendMessage('System', '영어 학습을 시작합니다. 질문이나 대화를 입력해주세요.');
});
