# 3.structured_output — 구조화 출력

응답을 정해진 스키마(JSON)로 강제해 바로 파싱합니다. `messages.parse()` + Pydantic 모델을
쓰면 `parsed_output`으로 검증된 객체를 바로 받습니다(지원: Opus 4.8 / Sonnet 4.6 / Haiku 4.5).

## 파일

| 파일 | 내용 |
|------|------|
| `1.structured_output.py` | `messages.parse()` + Pydantic — 스키마대로 파싱된 객체 받기 |

## 다른 벤더의 대응 기능

같은 개념을 벤더마다 다르게 구현합니다 — 비교해보면 API 설계 차이가 잘 보입니다.

| 위치 | 방식 |
|------|------|
| [`../../1.openai/6.structured_output/`](../../1.openai/6.structured_output/) | `response_format`/`json_schema`/Pydantic — 4단계 빌드업 |
| [`../../2.langchain/3.structured_output/`](../../2.langchain/3.structured_output/) | `with_structured_output()` — LangChain이 벤더 차이를 감춘 공통 인터페이스 |

## 설치

```bash
pip install anthropic python-dotenv pydantic
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
