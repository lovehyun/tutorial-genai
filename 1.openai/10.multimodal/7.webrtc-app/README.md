webrtc-whisper-app/
├── app.py                  ← Flask 서버
├── static/
│   ├── script.js           ← WebRTC + 마이크 전송 + 자막 처리
│   └── style.css
├── templates/
│   └── index.html          ← 화상 + 회의록 + 요약 UI
├── uploads/
│   └── [임시 오디오 저장]
├── whisper_utils.py        ← 로컬 whisper 전사 함수
└── .env

pip install git+https://github.com/openai/whisper.git
pip install torch
