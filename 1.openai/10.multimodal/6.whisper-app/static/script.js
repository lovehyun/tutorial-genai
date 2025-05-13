let mediaRecorder;
let audioChunks = [];

document.getElementById("recordBtn").onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
    
    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("audio", blob, "recording.webm");

        const res = await fetch("/transcribe", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        document.getElementById("result").innerText = data.transcript;
        audioChunks = [];
    };

    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 5000); // 5초 녹음
};
