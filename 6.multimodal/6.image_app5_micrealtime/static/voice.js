const micBtn = document.getElementById("micBtn");
let imageUploaded = false;

document.getElementById("imgForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = document.getElementById("image").files[0];
    if (!file) return alert("이미지를 선택해주세요.");

    const form = new FormData();
    form.append("image", file);

    const res = await fetch("/upload_img", {
        method: "POST",
        body: form
    });

    if (res.ok) {
        document.getElementById("uploadStatus").textContent = "✅ 이미지 업로드 완료!";
        imageUploaded = true;
    } else {
        document.getElementById("uploadStatus").textContent = "❌ 이미지 업로드 실패!";
    }
});

// ====== WebSocket 연결 ======
let voiceWS;
let audioCtx = new (window.AudioContext || window.webkitAudioContext)();
let stream, mediaRec;

function connectVoiceWS() {
    voiceWS = new WebSocket("ws://" + location.host + "/voice");
    voiceWS.binaryType = "arraybuffer";

    voiceWS.onopen = () => {
        console.log("voice ws open");
    };

    voiceWS.onclose = () => {
        console.log("voice ws closed");
        stopMic();  // 강제로 마이크도 끔
    };

    voiceWS.onmessage = async (event) => {
        if (typeof event.data === "string") {
            if (event.data === "NO_IMAGE") {
                alert("이미지를 먼저 업로드하세요.");
                voiceWS.close();
            }
            return;
        }

        try {
            const buffer = event.data;
            const audioBuffer = await audioCtx.decodeAudioData(buffer.slice(0));
            const source = audioCtx.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioCtx.destination);
            source.start();
        } catch (err) {
            console.error("오디오 재생 오류:", err);
        }
    };
}

// ====== 마이크 캡처 & 전송 ======
async function startMic() {
    if (!imageUploaded) {
        alert("이미지를 먼저 업로드해야 합니다.");
        return;
    }

    try {
        await new Audio().play().catch(() => {});  // user gesture 확보용 dummy
    } catch {}

    connectVoiceWS();

    stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true } });
    voiceStatus("ON");
    mediaRec = new MediaRecorder(stream, { mimeType: "audio/webm" });
    mediaRec.ondataavailable = e => {
        if (voiceWS.readyState === WebSocket.OPEN) {
            voiceWS.send(e.data);
        }
    };
    mediaRec.start(250);
}

function stopMic() {
    mediaRec?.stop();
    stream?.getTracks().forEach(t => t.stop());
    voiceStatus("OFF");
}

function voiceStatus(text) {
    const el = document.getElementById("voiceStatus");
    el.textContent = "마이크 " + text;
    el.className = "badge " + (text === "ON" ? "bg-danger" : "bg-secondary");
}

// ====== 마이크 버튼 이벤트 ======
micBtn.addEventListener("click", () => {
    if (mediaRec && mediaRec.state === "recording") stopMic();
    else startMic();
});
