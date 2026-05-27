# 구조화된 출력 (Structured Output)

LLM 응답을 **문자열 / 리스트 / JSON / Pydantic 객체** 등 원하는 형태로 받는 방법.

## 폴더 구조

```
3.structured_output/
├── 1.str_output_parser.py        ← StrOutputParser, CommaSeparatedListOutputParser (기본)
├── 2.pydantic_parser.py          ← PydanticOutputParser (prompt injection 방식)
├── 3.with_structured_output.py   ← .with_structured_output(Model) (LLM native, 권장)
├── 4.json_output_parser.py       ← JsonOutputParser (스키마 없는 가벼운 JSON)
└── README.md
```

## 학습 흐름

```
1.str_output_parser       ─ 기본 문자열/리스트 파싱
        ↓
2.pydantic_parser         ─ 스키마 강제 (Pydantic + format_instructions 주입 방식)
        ↓
3.with_structured_output  ─ LLM native 방식 (function calling 기반, 가장 권장)
        ↓
4.json_output_parser      ─ 가벼운 JSON dict (스키마 없음)
```

## 핵심: 두 가지 접근 방식

| 방식 | 어떻게? | 보장 수준 | 대상 |
|------|--------|---------|------|
| **(A) Prompt Injection** | `parser.get_format_instructions()` 를 prompt 에 끼워 "이런 형식으로 답해" 라고 지시 | 모델이 잘 따라야 함 (100% 보장 X) | 어떤 LLM 에도 동작 |
| **(B) LLM Native** | `.with_structured_output(Model)` — OpenAI function calling 을 내부적으로 사용 | 사실상 보장 (스키마 강제) | function calling 지원 LLM만 |

→ **OpenAI / Anthropic 등 function calling 지원 모델이면 (B) `with_structured_output()` 권장**.
오픈소스 LLM 이라 function calling 지원이 약하면 (A) `PydanticOutputParser` 사용.

## 파일별 상세

| 파일 | 클래스 / 메서드 | 반환 타입 | 한 줄 요약 |
|------|---------------|---------|----------|
| `1.str_output_parser.py` | `StrOutputParser`, `CommaSeparatedListOutputParser` | `str` / `list[str]` | AIMessage → 문자열, 콤마 구분 응답 → 리스트 |
| `2.pydantic_parser.py` | `PydanticOutputParser` | Pydantic 객체 | prompt 에 schema 주입, 응답을 Pydantic 으로 파싱 |
| `3.with_structured_output.py` | `llm.with_structured_output(Model)` | Pydantic 객체 | LLM 이 직접 구조화 응답 — **현재 가장 권장** |
| `4.json_output_parser.py` | `JsonOutputParser` | `dict` | 스키마 없이 그냥 JSON dict — 빠른 프로토타입/동적 필드 |

## 선택 가이드

| 상황 | 추천 |
|------|------|
| 스키마 명확 + 타입 안전성 + 최고 신뢰성 | **`3` `with_structured_output()`** |
| 어떤 LLM 에도 동작 + 스키마 강제 | **`2` `PydanticOutputParser`** |
| 빠른 프로토타입 / 필드가 동적 | **`4` `JsonOutputParser`** |
| 자유로운 자연어 답변만 필요 | **`1` `StrOutputParser`** |

## 관련 폴더

- [`../2.prompts/`](../2.prompts/) — 입력(prompt) 만드는 영역. 짝
- [`../4.chaining/7.output_format/`](../4.chaining/7.output_format/) — `CommaSeparatedListOutputParser`, `JsonOutputParser` 가 체인 안에서 어떻게 동작하는지

## 실행

```bash
pip install langchain langchain-openai python-dotenv pydantic
python 3.with_structured_output.py
```
