# 3.stt — 음성 인식 (STT)

오디오를 입력으로 받아 **텍스트로 받아쓰기**합니다 (오디오 → 텍스트).
`1.whisper_stt/`(기본 스크립트) → `2.whisper_app/`(웹앱)로 구성됩니다.

| 디렉토리 | 구분 | 내용 |
|----------|------|------|
| [`1.whisper_stt/`](1.whisper_stt/) | 기본 | 오디오 파일/마이크 녹음 → 텍스트, Gradio 자막 앱 — 3개 스크립트 |
| [`2.whisper_app/`](2.whisper_app/) | 앱 | 오디오 업로드 → Whisper API → 텍스트(JSON)를 반환하는 Flask 웹앱 |

`2.whisper_app/`은 `1.whisper_stt/`의 받아쓰기 로직을 웹앱으로 감싼 것입니다.
음성 생성(TTS)은 [`../4.tts/`](../4.tts/), 실시간 다자간 음성 인식은 [`../5.realtime_voice/1.webrtc_app/`](../5.realtime_voice/1.webrtc_app/)을 참고하세요.
