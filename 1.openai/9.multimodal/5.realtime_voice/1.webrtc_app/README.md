# 실시간 회의록 앱 (WebRTC / WebSocket)

마이크 음성을 실시간으로 받아 자막을 만들고, 회의가 끝나면 전체 내용을
AI로 요약해 주는 Flask + WebSocket 웹앱입니다.

## 무엇을 하는 앱인가

- 브라우저에서 마이크 음성을 짧은 조각으로 녹음해 서버로 전송합니다.
- 서버가 음성을 텍스트로 받아쓰고(STT), 그 자막을 **접속한 모든 사용자에게** 실시간 방송합니다.
- 여러 사람의 발언이 하나의 회의록으로 누적됩니다.
- 버튼 한 번으로 회의록 전체를 GPT가 요약합니다.

즉, **실시간 자막 + 다자간 회의록 + AI 요약**을 합친 앱입니다.

## 사용 기술

| 구분 | 기술 |
|------|------|
| 백엔드 | Flask + Flask-SocketIO |
| 실시간 전송 | WebSocket — 서버가 자막을 모든 클라이언트로 push |
| 마이크 입력 | 브라우저 마이크 캡처(getUserMedia) → 오디오 조각 업로드 |
| 음성 인식(STT) | `whisper_utils.py` — 아래 3가지 모드 선택 가능 |
| 요약 | OpenAI GPT-4o-mini (`chat.completions`) |

### STT 모드 (`.env`의 `WHISPER_MODE`)

`whisper_utils.py`는 환경변수로 음성 인식 방식을 고를 수 있습니다:

| 모드 | 동작 |
|------|------|
| `openai_whisper` | OpenAI Whisper API 사용 (인터넷 필요, 설치 간단) |
| `local_wav` | 로컬 faster-whisper로 인식 (WAV 입력) |
| `local_webp` | 로컬 faster-whisper + ffmpeg로 WEBM→WAV 변환 후 인식 |

## 주요 기능 / 라우트

- `/` — 회의 화면 UI
- `/upload_audio` (POST) — 음성 조각 수신 → STT → 자막을 SocketIO로 방송 + 회의록 누적
- `/summary` (POST) — 누적된 회의록 전체를 GPT로 요약
- `caption` (SocketIO 이벤트) — 새 자막을 모든 접속자에게 실시간 전달

## 실행

```bash
pip install flask flask-socketio openai python-dotenv werkzeug
# 로컬 STT 모드 사용 시: pip install faster-whisper  (+ ffmpeg 설치 필요)
python app.py
# 브라우저에서 http://localhost:5000 접속
```

`.env` 설정:
```
OPENAI_API_KEY=sk-...
WHISPER_MODE=openai_whisper   # 또는 local_wav, local_webp
```
