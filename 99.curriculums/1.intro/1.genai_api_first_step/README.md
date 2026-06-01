# 생성형 AI API 첫걸음

## 과정 정보
- **기간**: 1일 (총 8시간)
- **난이도**: 입문
- **대상**: Python 기초 문법을 알고 있으나 생성형 AI API를 처음 사용하는 개발자
- **선수 과목**: 없음 (Python 기초, pip/venv 사용법 필요)

## 학습 목표
1. **REST API를 직접 호출**해 보며 LLM이 어떤 형식으로 요청·응답을 주고받는지 이해한다
2. 같은 호출을 **SDK로** 다시 작성하며, REST 대비 무엇이 추상화되는지 비교한다
3. **구버전(v0.x) ↔ 신버전(v1.x) SDK** 인터페이스 변화를 경험해, 라이브러리 업데이트에 따른 코드 변천을 직접 본다
4. 멀티턴 대화·Vision·Streaming·Structured Output·Gemini 등 입문에서 알아야 할 기본 기능을 한 바퀴 돈다

## 학습 철학 — 한 단계에 개념 하나씩

REST API를 처음부터 함수로 잘 추상화해 보여주면 편하지만, "왜 그렇게 짜는지"가 안 보입니다.
이 과정은 **가장 단순한 호출에서 시작**해, 한 파일에 새 개념을 하나씩만 더해 가며 진행합니다.

- 1~4단계: `requests`로 REST API를 직접 호출 — **HTTP·JSON·역할(role)·파라미터·예외처리·대화 루프**를 단계별로
- 5~7단계: 같은 일을 `openai` SDK로 — **구버전 → 신버전 → 파라미터 적용** 순서로
- 8~9단계: **멀티턴·Vision**으로 이후 챕터(챗봇 히스토리, 멀티모달)로 자연스럽게 연결

> 5·6단계를 일부러 **구·신 SDK로 나눈** 이유: 인터넷에 떠도는 옛 예제(`openai.ChatCompletion.create`)를
> 만났을 때 당황하지 않도록, 그리고 라이브러리 메이저 버전 업데이트가 코드를 어떻게 바꿔놓는지
> 실제로 한 번 겪어보기 위함입니다.

## 커리큘럼

### Day 1: REST → SDK → 응용

| 시간 | 단계 | 실습 파일 | 이 단계에서 새로 배우는 것 |
|------|------|-----------|---------------------------|
| 09:00-09:30 | 오리엔테이션 | — | 과정 소개, 가상환경 / `.env` 설정, OpenAI·Gemini API 키 발급 |
| 09:30-10:00 | **REST ①** 최소 호출 | `1.openai/1.intro/1.restapi_hello.py` | `requests.post`로 직접 호출, 응답 JSON 구조 통째로 확인 |
| 10:00-10:30 | **REST ②** content + 역할 | `1.openai/1.intro/2.restapi_content.py` | 답변(content) 추출, `system`/`user`/`assistant` 역할 |
| 10:45-11:15 | **REST ③** 응답 제어 파라미터 | `1.openai/1.intro/3.restapi_params.py` | `temperature`, `max_tokens`, `top_p`, `frequency/presence_penalty` |
| 11:15-12:00 | **REST ④** 완성형 | `1.openai/1.intro/4.restapi_chat.py` | 함수화, `try/except`, `input()` 대화 루프 — REST 방식의 마무리 |
| 13:00-13:45 | **SDK ⑤** 구버전(v0.x) | `1.openai/1.intro/10.sdk_old.py` | `openai.ChatCompletion.create()` — 옛 코드 읽기용 (`pip install openai==0.28`) |
| 13:45-14:15 | **SDK ⑥** 신버전(v1.x) | `1.openai/1.intro/11.sdk_new.py` | `OpenAI()` 클라이언트 + `client.chat.completions.create()` — 현재 표준 |
| 14:15-14:45 | **SDK ⑦** SDK 방식 파라미터 | `1.openai/1.intro/12.sdk_params.py` | REST의 `json={...}` ↔ SDK의 키워드 인자 비교, 표준/추론 모델 주의점 |
| 15:00-15:30 | **⑧** 멀티턴 대화 | `1.openai/1.intro/13.chat_multiturn.py` | `messages` 누적으로 대화 맥락 유지 → 이후 `3.chatbot2_history`로 연결 |
| 15:30-16:00 | **⑨** Vision — 이미지 입력 | `1.openai/1.intro/14.chat_vision.py` | `content`를 리스트로 (`text` + `image_url`) → 이후 `10.multimodal`로 연결 |
| 16:00-16:30 | Streaming 응답 | `1.openai/8.streaming/1.concept/1.sse_stream_template.py`, `2.sse_stream_restapi.py` | SSE로 토큰 단위 스트리밍 (SDK 템플릿 → REST 직접 호출) |
| 16:30-16:50 | Structured Output 맛보기 | `1.openai/9.structured_output/3.json_schema.py`, `5.func_calling_basic.py` | JSON Schema 강제 출력 / Function Calling — 구조화된 응답 |
| 16:50-17:00 | Gemini로 같은 호출 비교 | `7.google/1.basic/1.intro.py`, `2.chat.py` | 다른 프로바이더의 인터페이스 차이를 빠르게 살펴보기 |

## 환경 설정

```bash
pip install openai requests python-dotenv google-generativeai
```

API 키는 상위 폴더 `.env` 파일에 설정합니다:
```
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

> **구버전 SDK 실습 안내**: 5단계는 `openai==0.28`이 필요합니다.
> 신/구 충돌을 피하려면 별도 가상환경에서 실행하거나, 6단계 실행 전에 `pip install -U openai`로 되돌리세요.

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/01_genai_intro/01_genai_landscape.md` | 생성형 AI 생태계 개요 |
| `0.docs/01_genai_intro/02_llm_companies_models.md` | LLM 기업·모델 비교 |
| `0.docs/05_genai_advanced/01_openai_advanced.md` | OpenAI API 심화 |
| `0.docs/05_genai_advanced/03_gemini_api.md` | Gemini API |

## 참고 자료
- [OpenAI API 공식 문서](https://platform.openai.com/docs)
- [OpenAI Python SDK 마이그레이션 가이드 (v0 → v1)](https://github.com/openai/openai-python/discussions/742)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- `1.openai/1.intro/README.md` — REST/SDK 단계별 흐름과 표준·추론 모델 구분 정리
- `1.openai/8.streaming/README.md` — 스트리밍 응답 처리
- `1.openai/9.structured_output/README.md` — 구조화 출력 6단계
- `7.google/1.basic/` — Gemini 기초 예제 전체
