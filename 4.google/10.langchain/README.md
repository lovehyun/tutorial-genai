# 10.langchain — Gemini를 LangChain으로

`langchain-google-genai`의 `ChatGoogleGenerativeAI`로 Gemini를 LangChain 생태계
(프롬프트 템플릿, LCEL 체인, 구조화 출력) 안에서 다룹니다.

## 순서

| 파일 | 내용 |
|------|------|
| `1.intro.py` | `ChatGoogleGenerativeAI` 기본 호출 |
| `2.chain.py` | LCEL 체인 — `prompt \| llm \| parser` |
| `3.structured_output.py` | `with_structured_output()` |

## 설치

```bash
pip install langchain-google-genai langchain-core python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
