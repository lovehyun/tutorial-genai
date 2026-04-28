# 멀티모달 AI 입문

## 과정 정보
- **기간**: 1일 (총 8시간)
- **난이도**: 입문
- **대상**: OpenAI API 기초를 익힌 후 이미지·음성·실시간 처리를 경험하고 싶은 학습자
- **선수 과목**: 입문 1. 생성형 AI API 첫걸음

## 학습 목표
1. DALL-E API를 활용해 이미지를 생성·편집할 수 있다
2. Whisper API로 음성을 텍스트로 변환하고 자막 앱을 만들 수 있다
3. 이미지 생성 앱과 실시간 음성 처리 앱을 Gradio로 구현할 수 있다

## 커리큘럼

### Day 1: 이미지 생성 · 음성 인식 · 실시간 처리

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 멀티모달 AI 개요, 환경 설정 |
| 09:30-10:00 | DALL-E 이미지 생성 | `1.openai/10.multimodal/1.dall-e/1.openai_image.py` | 텍스트로 이미지 생성 기초 |
| 10:00-10:30 | DALL-E 다중 생성 & 편집 | `1.openai/10.multimodal/1.dall-e/2.openai_images.py`, `1.openai/10.multimodal/1.dall-e/3.openai_edit.py` | 다중 이미지, 이미지 편집 |
| 10:45-11:15 | DALL-E 마스크 & 고급 | `1.openai/10.multimodal/1.dall-e/4.openai_mask.py`, `1.openai/10.multimodal/1.dall-e/5.openai_image2.py` | 마스크 편집, 고급 생성 옵션 |
| 11:15-12:00 | 이미지 편집 앱 | `1.openai/10.multimodal/2.dall-e-app-edit/app.py`, `1.openai/10.multimodal/3.dall-e-app-gallery/app.py` | Gradio 기반 이미지 편집/갤러리 앱 |
| 13:00-13:45 | Whisper 음성→텍스트 | `1.openai/10.multimodal/5.whisper/1.audio2text.py`, `1.openai/10.multimodal/5.whisper/2.mic2text.py` | 파일/마이크 음성 인식 |
| 13:45-14:30 | 자막 & 음성 앱 | `1.openai/10.multimodal/5.whisper/3.subtitle_app.py`, `1.openai/10.multimodal/6.whisper-app/app.py` | 자막 생성 앱, Whisper 웹 앱 |
| 14:45-15:30 | 이미지+음성 통합 앱 | `1.openai/10.multimodal/4.image_app/app.py`, `1.openai/10.multimodal/4.image_app2_design/app.py` | 이미지 생성 + 음성 입력 통합 |
| 15:30-16:15 | 마이크 입출력 앱 | `1.openai/10.multimodal/4.image_app4_micinput/app.py`, `1.openai/10.multimodal/4.image_app4_micinputoutput/app.py` | 마이크 입력 → 이미지 생성 → 음성 출력 |
| 16:15-17:00 | WebRTC 실시간 처리 | `1.openai/10.multimodal/7.webrtc-app/app.py` | WebRTC 기반 실시간 음성 처리 앱, 종합 Q&A |

## 환경 설정

```bash
pip install openai gradio pydub pyaudio
```

## 참고 자료
- `1.openai/10.multimodal/1.dall-e/` — DALL-E 이미지 생성
- `1.openai/10.multimodal/2.dall-e-app-edit/` — 이미지 편집 앱
- `1.openai/10.multimodal/3.dall-e-app-gallery/` — 갤러리 앱
- `1.openai/10.multimodal/4.image_app*/` — 이미지 생성 앱 시리즈
- `1.openai/10.multimodal/5.whisper/` — 음성 인식
- `1.openai/10.multimodal/6.whisper-app/` — Whisper 웹 앱
- `1.openai/10.multimodal/7.webrtc-app/` — WebRTC 실시간 앱
