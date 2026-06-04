# 멀티모달 AI

OpenAI의 멀티모달 API(비전·이미지 생성·음성)를 활용한 예제 모음입니다.

각 모달리티는 **기본 스크립트(단독 실행) → 앱(Flask 등 복합)** 순서로 구성되어 있고,
앱 시리즈는 **단계별로 한 가지씩 기능을 더하며** 진화합니다 (텍스트 기본기는 [`../1.intro/`](../1.intro/)).

| 모달리티 | 방향 | 기본 | 앱 |
|----------|------|------|----|
| 비전(이미지 이해) | 이미지 → 텍스트 | `4.vision/` | `5.vision_app*` |
| 음성 인식(STT) | 오디오 → 텍스트 | `6.whisper_stt/` | `7.whisper_app/` |
| 음성 생성(TTS) | 텍스트 → 오디오 | `8.tts/` | — |
| 실시간 음성 | 오디오 ↔ 오디오 | — | `9.webrtc_app/` |
| 이미지 생성 | 텍스트 → 이미지 | `10.gpt_image/` | `11.gpt_image_app*` |

> ⚠️ **음악 생성은 OpenAI 미제공**입니다. 음악은 별도 [`6.musicgen`](../../6.musicgen/)(Meta MusicGen, 로컬)을 참고하세요.

---

## 이미지 생성 (DALL-E) — deprecated

> 🛑 `dall-e-2`·`dall-e-3`는 2026-05-12자로 API에서 제거되었습니다(개념 학습용 보존).
> 현행 이미지 생성은 `10.gpt_image/`(기본) · `11.gpt_image_app/`(앱)을 참고하세요.

| 디렉토리 | 설명 |
|----------|------|
| `1.dall-e(deprecated)/` | DALL-E 이미지 생성 기초 (6단계, 개념용) |
| `2.dall-e-app-edit(deprecated)/` | DALL-E 이미지 편집 웹앱 |
| `3.dall-e-app-gallery(deprecated)/` | DALL-E 갤러리 앱 |

---

## 비전 (이미지 이해)

이미지를 입력으로 받아 **설명·분석**합니다 (이미지 *생성*이 아님).

### 기본 — `4.vision/`
| 파일 | 내용 |
|------|------|
| `1.vision_url.py` | 인터넷 이미지 **URL** → 설명 (`chat.completions`에 text+image_url 블록) |
| `2.vision_localfile.py` | **로컬 파일** → base64 data URL → 분석 |
| `3.vision_question.py` | 한 이미지에 OCR·색상·분위기 등 **여러 질문** |

### 앱 — `5.vision_app*` (단계별 진화)
이미지를 업로드하면 GPT-4o(-mini)가 보고 설명합니다. 각 단계가 더하는 것:

| 단계 | 디렉토리 | 이 단계에서 새로 더해지는 것 |
|------|----------|------------------------------|
| 1 | `5.vision_app/` | 가장 단순 — **한 페이지**에서 이미지 업로드→설명 (`/` 라우트가 GET·POST 겸함) |
| 2 | `5.vision_app2_design/` | 라우트 **분리**(`/`=페이지, `/generate`=처리) + 결과를 **JSON**으로 반환(fetch) + UI 개선 |
| 3 | `5.vision_app3_clipboard/` | 사용자 **질문 입력**(`/ask`, "설명해줘" 고정 탈피) + **클립보드 붙여넣기**(Ctrl+V) |
| 4 | `5.vision_app4_micinput/` | **마이크 음성으로 질문**(브라우저 STT) + 업로드 **크기 제한·에러 핸들러** + `gpt-4o-mini`로 비용↓ |
| 5 | `5.vision_app5_micinputoutput/` | 답변을 **음성으로 출력(TTS)** — ★변화는 프론트(SpeechSynthesis)뿐, **백엔드는 4단계와 동일** |
| 6 | `5.vision_app6_micrealtime/` | **실시간 음성 대화** — 요청-응답 → **스트리밍**. Flask 대신 **Quart(비동기)** 사용 |

> 4~6단계의 음성 입력은 브라우저 `SpeechRecognition`(클라이언트 STT)입니다.
> 서버에서 Whisper로 인식하는 방식은 아래 `6.whisper_stt/`에서 다룹니다.

---

## 음성 — 인식(STT) · 생성(TTS) · 실시간

### 음성 인식(STT) 기본 — `6.whisper_stt/`
| 파일 | 내용 |
|------|------|
| `1.audio2text.py` | **오디오 파일** → 텍스트 (`audio.transcriptions`, `whisper-1`) |
| `2.mic2text.py` | **마이크로 N초 녹음**(sounddevice) → WAV → 받아쓰기 |
| `3.subtitle_app.py` | **Gradio** UI로 오디오 업로드 → 자막 생성 (이 폴더에서 유일하게 Gradio) |

### 음성 인식 앱 — `7.whisper_app/`
오디오 파일 업로드 → Whisper API → 텍스트(JSON) 반환하는 **Flask 웹앱**.
`6.whisper_stt/`(스크립트)를 웹앱으로 감싼 것. `/transcribe` 라우트, `secure_filename`, 한국어(`language="ko"`), 처리 후 임시파일 삭제.

### 음성 생성(TTS) 기본 — `8.tts/`
| 파일 | 내용 |
|------|------|
| `1.tts_basic.py` | 텍스트 → **mp3** (`audio.speech.create`) |
| `2.tts_voices.py` | 여러 **voice**(alloy/nova/onyx…) 비교 저장 |
| `3.tts_style_format.py` | `instructions`로 **말투/감정** 지정 + `response_format`(mp3/wav…) |

### 실시간 음성 앱 — `9.webrtc_app/`
**실시간 자막 + 다자간 회의록 + AI 요약** 앱 (Flask + **Flask-SocketIO**).
마이크 음성 조각 → STT → 자막을 **WebSocket으로 전체 방송** → 회의록 누적 → 버튼으로 GPT 요약.
`whisper_utils.py`로 STT 모드 선택(`WHISPER_MODE`): `openai_whisper`(API) / `local_wav` / `local_webp`(faster-whisper).

---

## 이미지 생성 (gpt-image)

텍스트를 입력으로 받아 **이미지를 생성**합니다.

### 기본 — `10.gpt_image/`
| 파일 | 내용 |
|------|------|
| `1.image_generate.py` | 프롬프트 → 생성 → PNG 저장 (`images.generate`, **base64 응답**) |
| `2.image_params.py` | `size` / `quality` 비교 |
| `3.image_transparent.py` | **투명 배경** PNG (아이콘/스티커) |

### 앱 — `11.gpt_image_app*` (단계별 진화)
`gpt-image-1.5`의 세 기능을 단계별로. 각 단계가 더하는 것:

| 단계 | 디렉토리 | 핵심 |
|------|----------|------|
| 1 | `11.gpt_image_app/` | **생성** — 프롬프트 → 이미지 (`images.generate`) |
| 2 | `11.gpt_image_app2_inpaint/` | **부분 편집(인페인팅)** — 영역 선택 → 그 부분만 재생성 (`images.edit` + **마스크**, 투명영역=편집대상) |
| 3 | `11.gpt_image_app3_consistency/` | **일관성 유지** — 기준 이미지 참고 → **같은 피사체**로 새 장면 (`images.edit`, **마스크 없음**) |

모델/가격 비교, 마스크·일관성 개념 상세는 [`11.gpt_image_app/README.md`](11.gpt_image_app/README.md) 참고.

---

## 설치

```bash
pip install openai flask pillow requests python-dotenv
# Whisper 마이크 입력: pip install sounddevice scipy
# 자막 앱(Gradio): pip install gradio
# 실시간 앱: pip install flask-socketio   (로컬 STT: faster-whisper + ffmpeg)
```

API 키는 `1.openai/.env`에 둡니다: `OPENAI_API_KEY=sk-...`
