# 멀티모달 AI

OpenAI의 멀티모달 API(이미지 생성, 음성 인식)를 활용한 예제 모음입니다.

## 디렉토리 구조

### 이미지 생성 (DALL-E) — deprecated

> 🛑 **`dall-e-2`·`dall-e-3`는 2025-11-14 단종 공지 후 2026-05-12자로 API에서 제거**되었습니다.
> 아래 `(deprecated)` 폴더들의 dall-e 예제는 그대로는 실행되지 않습니다(개념 학습용으로 보존).
> 현행 이미지 모델·가격은 `8.gpt_image_app/`을 참고하세요.

| 디렉토리 | 설명 |
|----------|------|
| `1.dall-e(deprecated)/` | DALL-E 이미지 생성 기초 — 6단계 빌드업 (생성→모델비교→배치→마스크→편집→gpt-image-1) |
| `2.dall-e-app-edit(deprecated)/` | Flask 기반 DALL-E 이미지 편집 웹앱 |
| `3.dall-e-app-gallery(deprecated)/` | Flask 기반 DALL-E 이미지 갤러리 앱 |

`1.dall-e(deprecated)/`의 단계별 학습 순서·이미지 모델 변경 내역은 그 폴더의 `README.md`를 참고하세요.

### 이미지 분석(Vision) 앱 (단계별 확장)

이미지를 업로드하면 GPT-4o가 보고 설명·분석하는 앱입니다 (이미지 *생성*이 아님).

| 디렉토리 | 설명 |
|----------|------|
| `4.vision_app/` | 기본 — 이미지 업로드 → GPT-4o 설명 |
| `4.vision_app2_design/` | API 분리 + UI 디자인 개선 |
| `4.vision_app3_clipboard/` | 질문 입력 + 클립보드 붙여넣기 |
| `4.vision_app4_micinput/` | 마이크 음성 입력 + 백엔드 견고화 |
| `4.vision_app5_micinputoutput/` | 음성 입력 + 음성 출력(TTS) |
| `4.vision_app6_micrealtime/` | 실시간 음성 대화 (WebRTC/WebSocket) |

> 위 앱의 음성 입력은 브라우저 `SpeechRecognition`(클라이언트 측 STT)을 씁니다.
> 서버에서 OpenAI Whisper API로 인식하는 방식은 아래 `5.whisper/`에서 다룹니다.

### 음성 인식 (Whisper)

| 디렉토리 | 설명 |
|----------|------|
| `5.whisper/` | Whisper API 음성 인식 (파일, 마이크, 자막) |
| `6.whisper-app/` | Flask 기반 Whisper 웹앱 |

`5.whisper/3.subtitle_app.py`만 Gradio를 사용합니다(나머지는 Flask). Gradio는
ML 데모용 UI를 자동 생성하는 프레임워크입니다.

### 실시간 통신

| 디렉토리 | 설명 |
|----------|------|
| `7.webrtc-app/` | 실시간 회의록 앱 (WebSocket 자막 + AI 요약) |

### gpt-image-1 활용 앱 (단계별 확장)

OpenAI 최신 이미지 모델 `gpt-image-1`의 기능을 단계별로 다룹니다.

| 디렉토리 | 설명 |
|----------|------|
| `8.gpt_image_app/` | 1단계 — 이미지 생성 |
| `8.gpt_image_app2_inpaint/` | 2단계 — 특정 영역만 편집 (인페인팅) |
| `8.gpt_image_app3_consistency/` | 3단계 — 주인공 유지하며 변형 |

자세한 설명은 [`8.gpt_image_app/README.md`](8.gpt_image_app/README.md) 참고.

## 설치

```bash
pip install openai flask pillow requests python-dotenv
# Whisper 마이크 입력: pip install sounddevice scipy
# 자막 앱(Gradio): pip install gradio
```
