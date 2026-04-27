# OpenAI API 입문

OpenAI API를 호출하는 세 가지 방식을 비교하며 배우는 입문 예제입니다.

## 핵심 개념

### API 호출 방식
- **REST API**: `requests` 라이브러리로 HTTP 요청을 직접 전송하는 방식
- **SDK (구버전)**: `openai.ChatCompletion.create()` — v0.x 스타일
- **SDK (신버전)**: `openai.OpenAI()` 클라이언트 인스턴스 — v1.x 스타일 (현재 표준)

### 주요 파라미터
| 파라미터 | 설명 | 범위 |
|----------|------|------|
| `temperature` | 창의성 제어 | 0.0(정확) ~ 2.0(창의) |
| `top_p` | 확률 기반 토큰 선택 | 0.0 ~ 1.0 |
| `max_tokens` | 최대 응답 길이 | 모델에 따라 다름 |
| `frequency_penalty` | 반복 억제 | -2.0 ~ 2.0 |
| `presence_penalty` | 새 주제 유도 | -2.0 ~ 2.0 |

## 예제 목록

| 파일 | 설명 |
|------|------|
| `1.restapi.py` | HTTP REST API 직접 호출 (requests) |
| `2.sdk_old.py` | OpenAI SDK 구버전 (v0.x) |
| `3.sdk_new.py` | OpenAI SDK 신버전 (v1.x) |
| `4.vision.py` | Vision API — 이미지 분석 (gpt-4o) |

## 실행

```bash
pip install openai python-dotenv
python 3.sdk_new.py
```
