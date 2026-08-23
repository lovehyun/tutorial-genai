# 2.structured_output — 구조화 출력

응답을 정해진 스키마(JSON)로 강제해 바로 파싱합니다. Pydantic 모델을 `response_schema`로
넘기면 검증된 객체를 바로 받습니다.

## 파일

| 파일 | 내용 |
|------|------|
| `1.structured_output.py` | Pydantic 스키마로 JSON 구조화 출력 강제 |

## 다른 벤더의 대응 기능

| 위치 | 방식 |
|------|------|
| [`../../1.openai/6.structured_output/`](../../1.openai/6.structured_output/) | `response_format`/`json_schema`/Pydantic — 4단계 빌드업 |
| [`../../2.langchain/3.structured_output/`](../../2.langchain/3.structured_output/) | `with_structured_output()` — 벤더 차이를 감춘 공통 인터페이스 |
| [`../../3.anthropic/3.structured_output/`](../../3.anthropic/3.structured_output/) | `messages.parse()` + Pydantic |

LangChain으로 같은 걸 하는 예제는 [`../10.langchain/3.structured_output.py`](../10.langchain/3.structured_output.py) 참고.

## 설치

```bash
pip install google-genai python-dotenv pydantic
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
