# OpenAI 구조화된 출력 예제

OpenAI API의 Function Calling과 Structured Output 기능 예제입니다.

## 예제 목록

| 파일 | 설명 |
|------|------|
| `1.function_calling.py` | Function Calling + JSON 모드 + 데이터 추출 |
| `2.json_schema.py` | JSON Schema strict mode + Pydantic parse() |

## 핵심 개념

- **Function Calling**: LLM이 정의된 함수를 자동으로 호출하여 외부 시스템과 연동
- **JSON Object 모드**: `response_format={"type": "json_object"}`로 JSON 응답 강제
- **JSON Schema (strict)**: `response_format={"type": "json_schema", ...}`로 스키마 100% 준수 강제
- **Pydantic parse()**: `client.beta.chat.completions.parse()`로 Pydantic 모델 직접 바인딩

## 설치 및 실행

```bash
pip install openai pydantic
python 1.function_calling.py
python 2.json_schema.py
```
