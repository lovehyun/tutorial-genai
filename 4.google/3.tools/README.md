# 3.tools — 도구 호출

모델이 스스로 못 하는 일을 도구에 위임하는 두 갈래 — **내가 만든 함수**(1) vs
**Google 서버가 실행하는 내장 도구**(2).

## 순서

| 파일 | 내용 |
|------|------|
| `1.function_calling.py` | 함수 호출 — 모델이 함수/인자를 판단, 실행은 내 코드가 함 |
| `2.code_execution.py` | 코드 실행(내장 도구) — Google 서버 샌드박스에서 직접 실행 |

## 다른 벤더의 대응 기능

| 위치 | 비교 |
|------|------|
| [`../../1.openai/7.function_calling/`](../../1.openai/7.function_calling/) | OpenAI의 함수 호출 |
| [`../../3.anthropic/2.tools/`](../../3.anthropic/2.tools/) | Anthropic의 클라이언트/서버 도구 — 동일한 2단 구조 |

검색·지도 같은 다른 내장 도구는 [`../8.grounding/`](../8.grounding/)에서 이어집니다.

## 설치

```bash
pip install google-genai python-dotenv
```

API 키는 `4.google/.env`에 설정합니다: `GOOGLE_API_KEY=...`
