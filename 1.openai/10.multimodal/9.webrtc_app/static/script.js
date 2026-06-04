// static/script.js
const socket = io();
const localVideo = document.getElementById('localVideo');
const remoteVideo = document.getElementById('remoteVideo');
const caption = document.getElementById('caption');
const log = document.getElementById('log');
const summaryOutput = document.getElementById('summary-output');

let localStream;
let peer;
let userName = prompt('당신의 이름을 입력하세요:', '사용자');

// WebRTC 연결 시작
async function initWebRTC() {
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    localVideo.srcObject = localStream;

    peer = new SimplePeer({ initiator: location.hash === '#1', trickle: false, stream: localStream });

    peer.on('signal', (data) => {
        socket.emit('signal', data);
    });

    socket.on('signal', (data) => {
        peer.signal(data);
    });

    peer.on('stream', (stream) => {
        remoteVideo.srcObject = stream;
    });
}

initWebRTC();

// 안정적인 오디오 녹음을 위해 stop → start 방식으로 녹음 구간 제어
let mediaRecorder;
let recordingTimer;
let isRecording = false;

const startBtn = document.getElementById('startRecording');
startBtn.onclick = () => {
    if (!isRecording) {
        const audioStream = new MediaStream(localStream.getAudioTracks());

        let options = {};
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
            options.mimeType = 'audio/webm;codecs=opus';
        }

        mediaRecorder = new MediaRecorder(audioStream, options);

        mediaRecorder.ondataavailable = async (e) => {
            if (!isRecording) return; // 녹음 중지 상태에서는 무시
            const blob = e.data;
            if (blob.size < 1000) {
                console.warn('Blob이 너무 작아서 무시됨.');
                return;
            }

            // 녹음 중일 때만 전송
            if (isRecording) {
                const timestamp = Date.now();
                const formData = new FormData();
                formData.append('audio', blob, `audio_${timestamp}.webm`);
                formData.append('user', userName);

                try {
                    const res = await fetch('/upload_audio', {
                        method: 'POST',
                        body: formData,
                    });
                    const data = await res.json();
                    console.log('서버 응답:', data);
                } catch (err) {
                    console.error('전송 실패:', err);
                }
            }
        };

        function recordChunk() {
            if (!isRecording) return;
            if (mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            mediaRecorder.start();
        }

        recordChunk();
        recordingTimer = setInterval(recordChunk, 7000);
        isRecording = true;
        startBtn.innerText = '녹음 중지';
    } else {
        isRecording = false;
        clearInterval(recordingTimer);
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }
        startBtn.innerText = '녹음 시작';
    }
};

// 자막 수신 및 회의록 표시
socket.on('caption', (data) => {
    caption.innerText = data.message;
    const li = document.createElement('li');
    li.innerText = data.message;
    log.appendChild(li);
});

// 회의 요약 요청
const summarizeBtn = document.getElementById('summarize');
summarizeBtn.onclick = async () => {
    const res = await fetch('/summary', { method: 'POST' });
    const data = await res.json();
    summaryOutput.innerText = data.summary;
};
