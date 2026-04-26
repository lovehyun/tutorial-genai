# OpenAI 구조화된 출력 예제

OpenAI API의 Function Calling과 Structured Output 기능 예제입니다.

## 예제 목록

| 파일 | 설명 |
|------|------|
| `1.function_calling.py` | Function Calling + JSON 모드 + 데이터 추출 |

## 핵심 개념

- **Function Calling**: LLM이 정의된 함수를 자동으로 호출하여 외부 시스템과 연동
- **Structured Output**: `response_format={"type": "json_object"}`로 JSON 응답 강제
- **데이터 추출**: Function Calling을 활용한 비정형 텍스트에서 구조화된 정보 추출

## 설치 및 실행

```bash
pip install openai
python 1.function_calling.py
```
