# 멀티모달 AI

OpenAI의 멀티모달 API(이미지 생성, 음성 인식)를 활용한 예제 모음입니다.

## 디렉토리 구조

### 이미지 생성 (DALL-E)

| 디렉토리 | 설명 |
|----------|------|
| `1.dall-e/` | DALL-E 이미지 생성 기초 (생성, 편집, 마스크) |
| `2.dall-e-app-edit/` | Flask 기반 DALL-E 이미지 편집 웹앱 |
| `3.dall-e-app-gallery/` | Flask 기반 DALL-E 이미지 갤러리 앱 |

### 이미지 생성 앱 (단계별 확장)

| 디렉토리 | 설명 |
|----------|------|
| `4.image_app/` | 기본 이미지 생성 앱 |
| `4.image_app2_design/` | UI 디자인 개선 |
| `4.image_app3_clipboard/` | 클립보드 복사 기능 |
| `4.image_app4_micinput/` | 마이크 음성 입력 추가 |
| `4.image_app4_micinputoutput/` | 음성 입출력 통합 |
| `4.image_app5_micrealtime/` | 실시간 음성 입력 |

### 음성 인식 (Whisper)

| 디렉토리 | 설명 |
|----------|------|
| `5.whisper/` | Whisper API 음성 인식 (파일, 마이크, 자막) |
| `6.whisper-app/` | Flask 기반 Whisper 웹앱 |

### 실시간 통신

| 디렉토리 | 설명 |
|----------|------|
| `7.webrtc-app/` | WebRTC 기반 실시간 음성/영상 앱 |

## 설치

```bash
pip install openai flask
# Whisper 마이크 입력: pip install pyaudio
```
