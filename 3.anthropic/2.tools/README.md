# 2.tools — 도구 호출 (Tool Use)

Claude가 스스로 못 하는 일을 "도구"에 위임하는 방법 두 갈래를 다룹니다 —
**내가 만든 함수를 내가 실행**(1~2) vs **Anthropic 서버가 알아서 실행**(3~4).

## 순서

### 클라이언트 도구 — 내가 만들고 내가 실행
| 파일 | 내용 |
|------|------|
| `1.tool_use.py` | 도구 호출 기본 — 수동 루프(요청 → 실행 → 결과 반환 → 최종 답) |
| `2.tool_runner.py` | tool runner(beta) — `@beta_tool` + 자동 루프로 1번을 간결하게 |

### 서버 도구 — Anthropic이 실행 (선언만 하면 됨)
| 파일 | 내용 |
|------|------|
| `3.web_search.py` | 웹 검색 — 모델이 알아서 검색하고 결과를 반영해 답함 |
| `4.code_execution.py` | 코드 실행 — 모델이 샌드박스에서 파이썬 코드를 돌려 계산/분석 |

> ⚠️ 서버 도구(3~4)는 별도 과금이 있을 수 있습니다. 문서를 확인하세요.

## 다른 벤더의 대응 기능

| 위치 | 비교 |
|------|------|
| [`../../1.openai/7.function_calling/`](../../1.openai/7.function_calling/) | OpenAI의 클라이언트 도구(1~2)에 해당 |
| [`../../1.openai/2.sdk/13.response_web_search.py`](../../1.openai/2.sdk/13.response_web_search.py) | OpenAI Responses API의 서버 도구 `web_search` — `3.web_search.py`와 비교해볼 것 |
| [`../../2.langchain/8.agents/1.builtin_tools/`](../../2.langchain/8.agents/1.builtin_tools/) | LangChain의 도구 카탈로그 — `get_all_tool_names()`로 뭐가 있는지 코드로 조회 가능 |

## 설치

```bash
pip install anthropic python-dotenv
```

API 키는 `3.anthropic/.env`에 설정합니다: `ANTHROPIC_API_KEY=sk-ant-...`
