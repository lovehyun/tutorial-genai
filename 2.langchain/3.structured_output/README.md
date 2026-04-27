# 구조화된 출력 (Structured Output)

LLM 응답을 문자열, 리스트, Pydantic 객체 등 원하는 형태로 파싱하는 방법을 학습합니다.

## 핵심 개념

### 출력 파서 종류
| 파서 | 설명 |
|------|------|
| `StrOutputParser` | AIMessage → 순수 문자열 |
| `CommaSeparatedListOutputParser` | 쉼표 구분 응답 → 파이썬 리스트 |
| `PydanticOutputParser` | JSON 응답 → Pydantic 객체 |
| `.with_structured_output()` | LLM 네이티브 구조화 출력 (최신 방식) |

### 학습 순서
1. **기본 파서** — `StrOutputParser`, `CommaSeparatedListOutputParser`
2. **Pydantic 파서** — `PydanticOutputParser` + `format_instructions`
3. **최신 방식** — `.with_structured_output(PydanticModel)` (별도 파서 불필요)

## 예제 목록

| 파일 | 설명 |
|------|------|
| `1.str_output_parser.py` | StrOutputParser, CommaSeparatedListOutputParser 기본 사용법 |
| `2.pydantic_parser.py` | PydanticOutputParser + format_instructions 주입 |
| `3.with_structured_output.py` | `.with_structured_output()` 최신 구조화 출력 |

## 실행

```bash
pip install langchain langchain-openai python-dotenv pydantic
python 1.str_output_parser.py
```
