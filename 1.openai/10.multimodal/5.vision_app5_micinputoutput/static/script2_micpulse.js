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
        const answer = data.answer || '응답 오류!';
        answerBox.textContent = answer;

        /* 답변 읽어주기 */
        speakAnswer(answer);
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

        startVisualizer();
    };

    recognition.onend = () => {
        recognizing = false;
        micBtn.classList.remove('active', 'pulsing');
        
        micBtn.innerHTML = '<i class="bi bi-mic-fill text-danger"></i>';
        // micBtn.textContent = '🎤';  // 마이크 아이콘 복귀

        stopVisualizer();
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

// 마이크 입력시 소리에 따라 마이크 펄스 그래프 추가
let audioCtx, analyser, micStream;
const canvas = document.getElementById('waveform');
const ctx = canvas.getContext('2d');

async function startVisualizer() {
    canvas.style.display = 'block';

    // 마이크 권한 요청
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    micStream = stream;

    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();

    const source = audioCtx.createMediaStreamSource(stream);
    source.connect(analyser);

    analyser.fftSize = 2048;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        requestAnimationFrame(draw);

        analyser.getByteTimeDomainData(dataArray);

        ctx.fillStyle = "#fff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.lineWidth = 2;
        ctx.strokeStyle = "#3498db";
        ctx.beginPath();

        const sliceWidth = canvas.width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * canvas.height / 2;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
    }

    draw();
}

function stopVisualizer() {
    canvas.style.display = 'none';
    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
    }
    if (audioCtx) {
        audioCtx.close();
    }
}

// 7) 음성 인식 기능 (Text-to-Speech)
function speakAnswer(text){
    /* 중복 재생 방지 */
    window.speechSynthesis.cancel();

    const utter = new SpeechSynthesisUtterance(text);

    /* 언어 자동 감지 (한글 여부) */
    const isKorean = /[ㄱ-ㅎㅏ-ㅣ가-힣]/.test(text);

    utter.lang = isKorean ? 'ko-KR' : 'en-US';

    /* 음성 선택 - 콘솔에서 실행 후 확인 */
    // speechSynthesis.getVoices().forEach(v => console.log(`${v.lang} - ${v.name}`));

    const preferredVoices = isKorean
        ? ['Google 한국의', 'Microsoft Heami']
        : ['Google US English', 'Microsoft Zira', 'Microsoft Mark'];

    // 가능한 음성 중 첫 번째 매칭되는 것 선택
    const voice = speechSynthesis.getVoices().find(v =>
        v.lang === utter.lang && preferredVoices.includes(v.name)
    );
    
    if (voice) utter.voice = voice;

    utter.rate  = 1.0;
    utter.pitch = 1.0;

    speechSynthesis.speak(utter);
}

/* iOS 등 일부 브라우저는 getVoices()가 늦게 채워집니다. */
if (typeof speechSynthesis !== 'undefined' &&
    speechSynthesis.onvoiceschanged !== undefined){
    speechSynthesis.onvoiceschanged = () => {};  // 초기 로드 트리거
}
