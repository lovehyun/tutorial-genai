# Whisper 음성 인식 웹앱

오디오 파일을 업로드하면 OpenAI Whisper API가 텍스트로 받아쓰는(STT) Flask 웹앱입니다.

## 무엇을 하는 앱인가

- 사용자가 오디오 파일(mp3, wav, m4a 등)을 업로드합니다.
- 서버가 OpenAI Whisper API로 음성을 한국어 텍스트로 변환합니다.
- 변환된 전사 결과를 화면에 표시합니다.

`5.whisper/`가 스크립트 단위 예제라면, 이 폴더는 그것을 **웹앱 형태**로 감싼 것입니다.

## 사용 기술

| 구분 | 기술 |
|------|------|
| 백엔드 | Flask |
| 음성 인식 | OpenAI Whisper API (`audio.transcriptions`, 모델 `whisper-1`) |
| 파일 처리 | werkzeug `secure_filename` — 안전한 업로드 파일명 처리 |

## 주요 기능 / 라우트

- `/` — 오디오 업로드 폼 페이지
- `/transcribe` (POST) — 오디오 파일 → Whisper API → 텍스트(JSON) 반환
- `language="ko"`로 한국어 인식, `response_format="text"`
- 전사가 끝나면 업로드된 임시 파일은 서버에서 삭제

## 실행

```bash
pip install flask openai python-dotenv
python app.py
# 브라우저에서 http://localhost:5000 접속
```

`.env`(상위 폴더)에 `OPENAI_API_KEY`를 설정하세요.
