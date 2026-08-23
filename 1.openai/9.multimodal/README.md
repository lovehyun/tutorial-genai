# 멀티모달 AI

OpenAI의 멀티모달 API(비전·이미지 생성·음성)를 활용한 예제 모음입니다.

각 그룹은 하위 폴더로 나뉘며, 폴더 안은 **기본 스크립트(단독 실행) → 앱(Flask 등 복합)** 순서로 구성되어 있고,
앱 시리즈는 **단계별로 한 가지씩 기능을 더하며** 진화합니다.
(텍스트 기본기는 `1.openai/1.restapi/`, `1.openai/2.sdk/` 참고.)

| 그룹 | 방향 | 내용 |
|------|------|------|
| [`1.vision/`](1.vision/) | 이미지 → 텍스트 | 이미지 이해 (기본 3개 + 앱 6단계) |
| [`2.image_generation/`](2.image_generation/) | 텍스트 → 이미지 | DALL-E(구) + gpt-image (기본 3개 + 앱 3단계) |
| [`3.stt/`](3.stt/) | 오디오 → 텍스트 | Whisper 음성 인식 (기본 + 앱) |
| [`4.tts/`](4.tts/) | 텍스트 → 오디오 | 음성 생성 (3개 스크립트) |
| [`5.realtime_voice/`](5.realtime_voice/) | 오디오 ↔ 오디오 | 실시간 다자간 회의록 + gpt-4o-audio 대화 |

> 비전(이미지 이해)과 이미지 생성을 나란히 두었습니다. 음성(인식·생성·실시간)은 뒤에 모았습니다.
>
> ⚠️ **음악 생성은 OpenAI 미제공**입니다. 음악은 별도 [`21.musicgen`](../../21.musicgen/)(Meta MusicGen, 로컬)을 참고하세요.

---

## 이미지 생성 (DALL-E) — deprecated

> 🛑 `dall-e-2`·`dall-e-3`는 2026-05-12자로 API에서 제거되었습니다(개념 학습용 보존).
> 현행 이미지 생성은 `2.image_generation/4.gpt_image/`(기본) · `2.image_generation/5.gpt_image_app/`(앱)을 참고하세요.

| 디렉토리 | 설명 |
|----------|------|
| `2.image_generation/1.dall-e(deprecated)/` | DALL-E 이미지 생성 기초 (6단계, 개념용) |
| `2.image_generation/2.dall-e-app-edit(deprecated)/` | DALL-E 이미지 편집 웹앱 |
| `2.image_generation/3.dall-e-app-gallery(deprecated)/` | DALL-E 갤러리 앱 |

---

## 비전 (이미지 이해)

이미지를 입력으로 받아 **설명·분석**합니다 (이미지 *생성*이 아님).

### 기본 — `1.vision/1.vision/`
| 파일 | 내용 |
|------|------|
| `1.vision_url.py` | 인터넷 이미지 **URL** → 설명 (`chat.completions`에 text+image_url 블록) |
| `2.vision_localfile.py` | **로컬 파일** → base64 data URL → 분석 |
| `3.vision_question.py` | 한 이미지에 OCR·색상·분위기 등 **여러 질문** |

### 앱 — `1.vision/2.vision_app*` (단계별 진화)
이미지를 업로드하면 GPT-4o(-mini)가 보고 설명합니다. 각 단계가 더하는 것:

| 단계 | 디렉토리 | 이 단계에서 새로 더해지는 것 |
|------|----------|------------------------------|
| 1 | `1.vision/2.vision_app/` | 가장 단순 — **한 페이지**에서 이미지 업로드→설명 (`/` 라우트가 GET·POST 겸함) |
| 2 | `1.vision/2.vision_app2_design/` | 라우트 **분리**(`/`=페이지, `/generate`=처리) + 결과를 **JSON**으로 반환(fetch) + UI 개선 |
| 3 | `1.vision/2.vision_app3_clipboard/` | 사용자 **질문 입력**(`/ask`, "설명해줘" 고정 탈피) + **클립보드 붙여넣기**(Ctrl+V) |
| 4 | `1.vision/2.vision_app4_micinput/` | **마이크 음성으로 질문**(브라우저 STT) + 업로드 **크기 제한·에러 핸들러** + `gpt-4o-mini`로 비용↓ |
| 5 | `1.vision/2.vision_app5_micinputoutput/` | 답변을 **음성으로 출력(TTS)** — ★변화는 프론트(SpeechSynthesis)뿐, **백엔드는 4단계와 동일** |
| 6 | `1.vision/2.vision_app6_micrealtime/` | **실시간 음성 대화** — 요청-응답 → **스트리밍**. Flask 대신 **Quart(비동기)** 사용 |

> 4~6단계의 음성 입력은 브라우저 `SpeechRecognition`(클라이언트 STT)입니다.
> 서버에서 Whisper로 인식하는 방식은 아래 `3.stt/1.whisper_stt/`에서 다룹니다.

---

## 이미지 생성 (gpt-image)

텍스트를 입력으로 받아 **이미지를 생성**합니다. (비전과 짝 — 한쪽은 읽기, 한쪽은 그리기)

### 기본 — `2.image_generation/4.gpt_image/`
| 파일 | 내용 |
|------|------|
| `1.image_generate.py` | 프롬프트 → 생성 → PNG 저장 (`images.generate`, **base64 응답**). gpt-image-1.5 vs 2 비교 주석 포함 |
| `2.image_params.py` | `size` / `quality` 비교 |
| `3.image_transparent.py` | **투명 배경** PNG (아이콘/스티커) — gpt-image-1.5 전용 기능 |

### 앱 — `2.image_generation/5.gpt_image_app*` (단계별 진화)
`gpt-image-1.5`의 세 기능을 단계별로. 각 단계가 더하는 것:

| 단계 | 디렉토리 | 핵심 |
|------|----------|------|
| 1 | `2.image_generation/5.gpt_image_app/` | **생성** — 프롬프트 → 이미지 (`images.generate`) |
| 2 | `2.image_generation/5.gpt_image_app2_inpaint/` | **부분 편집(인페인팅)** — 영역 선택 → 그 부분만 재생성 (`images.edit` + **마스크**, 투명영역=편집대상) |
| 3 | `2.image_generation/5.gpt_image_app3_consistency/` | **일관성 유지** — 기준 이미지 참고 → **같은 피사체**로 새 장면 (`images.edit`, **마스크 없음**) |

모델/가격 비교, 마스크·일관성 개념 상세는 [`2.image_generation/5.gpt_image_app/README.md`](2.image_generation/5.gpt_image_app/README.md) 참고.

---

## 음성 — 인식(STT) · 생성(TTS) · 실시간

### 음성 인식(STT) 기본 — `3.stt/1.whisper_stt/`
| 파일 | 내용 |
|------|------|
| `1.audio2text.py` | **오디오 파일** → 텍스트 (`audio.transcriptions`, `whisper-1`) |
| `2.mic2text.py` | **마이크로 N초 녹음**(sounddevice) → WAV → 받아쓰기 |
| `3.subtitle_app.py` | **Gradio** UI로 오디오 업로드 → 자막 생성 (이 폴더에서 유일하게 Gradio) |

### 음성 인식 앱 — `3.stt/2.whisper_app/`
오디오 파일 업로드 → Whisper API → 텍스트(JSON) 반환하는 **Flask 웹앱**.
`3.stt/1.whisper_stt/`(스크립트)를 웹앱으로 감싼 것. `/transcribe` 라우트, `secure_filename`, 한국어(`language="ko"`), 처리 후 임시파일 삭제.

### 음성 생성(TTS) 기본 — `4.tts/`
| 파일 | 내용 |
|------|------|
| `1.tts_basic.py` | 텍스트 → **mp3** (`audio.speech.create`) |
| `2.tts_voices.py` | 여러 **voice**(alloy/nova/onyx…) 비교 저장 |
| `3.tts_style_format.py` | `instructions`로 **말투/감정** 지정 + `response_format`(mp3/wav…) |

> ⚠️ STT(받아쓰기)는 **Whisper**, TTS(음성 생성)는 **별개 모델**(`gpt-4o-mini-tts`)입니다 — 같은 "음성"이라도 서로 다른 API.

### 실시간 음성 앱 — `5.realtime_voice/1.webrtc_app/`
**실시간 자막 + 다자간 회의록 + AI 요약** 앱 (Flask + **Flask-SocketIO**).
마이크 음성 조각 → STT → 자막을 **WebSocket으로 전체 방송** → 회의록 누적 → 버튼으로 GPT 요약.
`whisper_utils.py`로 STT 모드 선택(`WHISPER_MODE`): `openai_whisper`(API) / `local_wav` / `local_webp`(faster-whisper).

### 음성 대화 — `5.realtime_voice/2.audio_chat/` (gpt-4o-audio)
**오디오 입력 → 오디오 출력을 모델 하나로** (STT+TTS 2단계가 아니라 단일 멀티모달 모델).
`1.audio_output`(텍스트→음성) · `2.audio_input`(오디오→이해·요약) · `3.voice_chat`(음성→음성 한 턴) · `4.voice_chat_loop`(**연속 대화** — 자동 재생+맥락 유지).
> STT(`3.stt/1.whisper_stt`)는 받아쓰기만, TTS(`4.tts`)는 읽어주기만 — `5.realtime_voice/2.audio_chat`은 한 모델이 **이해하고 답까지**.

---

## 설치

```bash
pip install openai flask pillow requests python-dotenv
# Whisper 마이크 입력: pip install sounddevice scipy
# 자막 앱(Gradio): pip install gradio
# 실시간 앱: pip install flask-socketio   (로컬 STT: faster-whisper + ffmpeg)
```

API 키는 `1.openai/.env`에 둡니다: `OPENAI_API_KEY=sk-...`
