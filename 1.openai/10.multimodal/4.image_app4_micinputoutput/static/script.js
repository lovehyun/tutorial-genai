// DOM 요소 캐싱
const qBox      = document.getElementById('questionBox');   // 질문 입력창(<textarea>)
const addBtn    = document.getElementById('addImgBtn');     // "이미지 추가" 버튼
const imgInput  = document.getElementById('imgInput');      // 숨겨진 <input type="file">
const preview   = document.getElementById('preview');       // 이미지 미리보기 <img>
const sendBtn   = document.getElementById('sendBtn');       // "질문 보내기" 버튼
const progress  = document.getElementById('progressBar');   // 진행바(로딩 표시)
const answerBox = document.getElementById('answerBox');     // GPT 응답 표시 영역

let attachedImage = null;  // 사용자가 첨부한 이미지 Blob/File 저장용 변수 (null이면 첨부 안된 상태)

// 1) "이미지 추가" 버튼 클릭 → 숨겨진 파일 입력창 열기
addBtn.addEventListener('click', () => imgInput.click());

// 2) 파일 선택 시 → handleImage() 호출해 미리보기 세팅
imgInput.addEventListener('change', (e) => handleImage(e.target.files[0]));

// 3) Ctrl+V(또는 ⌘+V) 이미지 붙여넣기 처리
//    - Clipboard API로 이미지 MIME 타입 찾기
//    - getAsFile() 로 Blob 변환 후 handleImage() 재사용
document.addEventListener('paste', (e) => {
    const item = [...e.clipboardData.items].find(i => i.type.startsWith('image/'));
    if (item) {
        handleImage(item.getAsFile());
        e.preventDefault(); // 기본 붙여넣기(텍스트) 동작 방지
    }
});

// 이미지 파일 → 미리보기로 표시하는 로직
function handleImage(file) {
    if (!file || !file.type.startsWith('image/')) return;  // 이미지가 아니면 무시
    attachedImage = file;                                  // 전역 변수에 저장

    // FileReader 로 Base64 DataURL 생성 → <img> 미리보기
    const reader = new FileReader();
    reader.onload = e => {
        preview.src   = e.target.result;  // DataURL
        preview.style.display = 'block';  // 보이도록
    };
    reader.readAsDataURL(file);
}

// 4) "질문 보내기" 버튼 → GPT 호출
sendBtn.addEventListener('click', async () => {
    const question = qBox.value.trim();

    // 유효성 검사
    if (!question)        { alert('질문을 입력하세요');  return; }
    if (!attachedImage)   { alert('이미지를 첨부하세요'); return; }

    // UI 잠금 + 로딩바 표시
    toggleLoading(true);

    // FormData에 텍스트 & 이미지 동시 전송
    const fd = new FormData();
    fd.append('question', question);
    fd.append('image',    attachedImage);

    try {
        const res  = await fetch('/ask', { method: 'POST', body: fd });
        const data = await res.json();
        // 서버가 반환한 GPT 답변 표시
        answerBox.textContent = data.answer || '응답 오류!';
    } catch (err) {
        console.error(err);
        answerBox.textContent = '서버 오류!';
    } finally {
        // UI 잠금 해제 + 로딩바 숨김
        toggleLoading(false);
    }
});

// 5) 로딩 상태 토글 함수
function toggleLoading(isLoading) {
    // 버튼 활성/비활성
    sendBtn.disabled   = isLoading;
    sendBtn.textContent = isLoading ? 'GPT 응답을 기다리는 중...' : '질문 보내기';

    // 진행바 표시/숨김
    progress.style.display = isLoading ? 'block' : 'none';
}

// 6) 음성 인식 기능
const micBtn = document.getElementById('micBtn');

let recognizing = false;
let recognition;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'ko-KR';              // 한국어 설정
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        recognizing = true;
        micBtn.classList.add('active', 'pulsing');

        micBtn.innerHTML = '<i class="bi bi-mic-fill text-danger"></i>';
        // micBtn.textContent = '🛑';  // 종료 아이콘
    };

    recognition.onend = () => {
        recognizing = false;
        micBtn.classList.remove('active', 'pulsing');
        
        micBtn.innerHTML = '<i class="bi bi-mic-fill text-danger"></i>';
        // micBtn.textContent = '🎤';  // 마이크 아이콘 복귀
    };

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        // qBox.value += text; // textarea에 입력 추가
        qBox.value += (qBox.value.trim() ? '\n' : '') + text; // 줄바꿈 후 추가
    };
} else {
    micBtn.disabled = true;

    micBtn.innerHTML = '<i class="bi bi-mic-slash text-muted"></i> 음성 미지원';
    // micBtn.textContent = '🎤 (불가)';
    console.warn('이 브라우저는 음성 인식을 지원하지 않습니다.');
}

// 마이크 버튼 클릭 시 인식 시작/중단
micBtn.addEventListener('click', () => {
    if (!recognition) return;
    if (recognizing) {
        recognition.stop();
    } else {
        recognition.start();
    }
});
