# 생성형 AI API 첫걸음

## 과정 정보
- **기간**: 1일 (총 8시간)
- **난이도**: 입문
- **대상**: Python 기초 문법을 알고 있으나 생성형 AI API를 처음 사용하는 개발자
- **선수 과목**: 없음 (Python 기초, pip/venv 사용법 필요)

## 학습 목표
1. REST API와 SDK 방식의 차이를 이해하고 직접 호출할 수 있다
2. OpenAI와 Gemini 두 프로바이더의 API를 사용할 수 있다
3. Vision(이미지 입력), Streaming, Structured Output을 활용할 수 있다

## 커리큘럼

### Day 1: API 기초부터 고급 기능까지

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 과정 소개, 환경 설정, API 키 발급 |
| 09:30-10:30 | OpenAI REST API | `1.openai/1.intro/1.restapi.py` | requests 라이브러리로 직접 API 호출 |
| 10:45-11:15 | OpenAI SDK (Legacy) | `1.openai/1.intro/2.sdk_old.py` | openai 라이브러리 기본 사용법 |
| 11:15-12:00 | OpenAI SDK (Modern) | `1.openai/1.intro/3.sdk_new.py` | 최신 SDK 패턴, ChatCompletion |
| 13:00-13:45 | OpenAI Vision | `1.openai/1.intro/4.vision.py` | 이미지 입력을 활용한 멀티모달 호출 |
| 13:45-14:30 | Streaming 응답 처리 | `1.openai/8.streaming/1.sse_stream.py` | SSE 기반 스트리밍 응답 구현 |
| 14:45-15:30 | Structured Output | `1.openai/9.structured_output/1.function_calling.py`, `1.openai/9.structured_output/2.json_schema.py` | Function Calling과 JSON Schema 출력 |
| 15:30-16:15 | Gemini API 기초 | `7.google/1.basic/1.intro.py`, `7.google/1.basic/2.chat.py` | Google Gemini API 기본 호출과 채팅 |
| 16:15-17:00 | Gemini 스트리밍 & 종합 실습 | `7.google/1.basic/4.stream.py`, `7.google/1.basic/5.structured_output.py` | Gemini 스트리밍, Structured Output, 종합 Q&A |

## 환경 설정

```bash
pip install openai google-generativeai requests
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/01_genai_intro/01_genai_landscape.md` | 생성형 AI 생태계 개요 |
| `0.docs/01_genai_intro/02_llm_companies_models.md` | LLM 기업과 모델 비교 |
| `0.docs/05_genai_advanced/01_openai_advanced.md` | OpenAI API 심화 |
| `0.docs/05_genai_advanced/03_gemini_api.md` | Gemini API |

## 참고 자료
- [OpenAI API 공식 문서](https://platform.openai.com/docs)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- `1.openai/1.intro/` — OpenAI 기초 예제 전체
- `7.google/1.basic/` — Gemini 기초 예제 전체
