# 미들웨어 (Middleware)

`create_agent(middleware=[...])` 로 끼우는 **플러그인** — 모델/도구 호출의 전후에 개입합니다.
langchain 1.x 에서 **요약·HITL·가드레일·재시도·한도** 같은 기능이 모두 미들웨어로 통일됐습니다.

| 파일 | 미들웨어 | 용도 |
|---|---|---|
| `12.1_summarization.py` | `SummarizationMiddleware` | 긴 대화를 요약으로 압축 (컨텍스트 관리) |
| `12.2_pii_guardrail.py` | `PIIMiddleware` | 이메일·카드번호 등 민감정보 마스킹/차단 (가드레일) |
| `12.3_custom_middleware.py` | `AgentMiddleware` 상속 | 직접 작성 — `before_model` / `after_model` 훅 |

## 내장 미들웨어 (일부)

| 클래스 | 하는 일 | 관련 예제 |
|---|---|---|
| `SummarizationMiddleware` | 오래된 메시지 요약 압축 | `12.1` |
| `PIIMiddleware` | PII 탐지·마스킹·차단 | `12.2` |
| `ToolRetryMiddleware` | 도구 일시 오류 자동 재시도 | `../4.internals/4.4` |
| `HumanInTheLoopMiddleware` | 도구 실행 전 사람 승인 | (비교) `../6.hitl_streaming/` |
| `ModelCallLimitMiddleware` / `ToolCallLimitMiddleware` | 호출 횟수 상한 | (비교) `../4.internals/4.3` |
| `ModelFallbackMiddleware` | 실패 시 대체 모델로 폴백 | — |

## 훅 (커스텀 미들웨어)

`AgentMiddleware` 를 상속하고 필요한 훅만 오버라이드:

| 훅 | 시점 |
|---|---|
| `before_model(state, runtime)` | 모델 호출 직전 (입력 검사/수정) |
| `after_model(state, runtime)` | 모델 응답 직후 (출력 로깅/후처리) |
| `wrap_model_call` / `wrap_tool_call` | 모델/도구 호출을 통째로 감싸기 |
| `before_agent` / `after_agent` | 에이전트 실행 시작/끝 |

> 데코레이터 형태(`@before_model`)로도 작성 가능합니다.

## 관련 폴더

- [`../6.hitl_streaming/`](../6.hitl_streaming/) — `interrupt_before` 방식 HITL (미들웨어 `HumanInTheLoopMiddleware` 와 비교)
- [`../4.internals/4.4_tool_errors.py`](../4.internals/) — `ToolRetryMiddleware`
- [`../5.langgraph_memory/5.5_trim_messages.py`](../5.langgraph_memory/) — 미들웨어 없이 메시지 trim
