# 멀티 에이전트 (Multi-Agent)

도구가 너무 많아지거나 도메인이 갈리면, **여러 전문 에이전트로 나누고** 한 에이전트가
다른 에이전트에게 일을 위임하게 만듭니다.

| 파일 | 패턴 | 그래프 | 설명 |
|---|---|---|---|
| `10.1_agent_as_tool.py` | Agent-as-Tool | 내장(자동) | 전문 에이전트를 `@tool` 로 포장해 호출. `create_agent` 가 자동 구성한 그래프를 '도구처럼' 재사용 (가장 단순) |
| `10.2_supervisor.py` | Supervisor | **StateGraph 직접** | `START`/`END` + 조건부 엣지로 '관리자 ↔ worker' 루프를 손으로 구성 |
| `10.3_finance_analyst.py` | 병렬 분석가 | **StateGraph 직접** | 주가(yfinance) worker + 뉴스 worker 를 **병렬**로 돌려(fan-out) 합류(fan-in) 후 종합 |

## create_agent vs StateGraph — 언제 START/END 를 직접 짜나?

> **`create_agent`(현행 `langchain.agents`) 가 내부에서 LangGraph 그래프**(`START → model → tools → END`)를
> **자동 구성**합니다. 따라서 **단일 에이전트(LLM + 도구, 표준 ReAct 루프)** 라면 그래프를 손으로 짤 필요가 없습니다 — `10.1`.
>
> ⚠️ 헷갈리기 쉬운 점: 여기서 "내장/자동 구성" 은 **함수 `create_agent` 의 동작**을 말합니다.
> 옛 `langgraph.prebuilt.create_react_agent`(deprecated 모듈)와는 무관 — 그건 `create_agent` 로 **대체된** 구버전입니다.

직접 `StateGraph`(노드/엣지/`START`/`END`)를 짜는 건, `create_agent` 의 **고정된 ReAct 모양으로
표현할 수 없는 흐름**이 필요할 때입니다:

| 필요한 흐름 | 예제 |
|---|---|
| 여러 worker를 **조건부로 라우팅**하고 루프 | `10.2_supervisor` |
| 여러 작업을 **병렬 실행 → 합류**(fan-out/fan-in) | `10.3_finance_analyst` |
| 동적 작업 분해 / 생성→평가→개선 루프 | `../9.agentic_patterns/9.4`, `9.5` |

정리하면 — **단일 에이전트 = `create_agent`(START/END 불필요), 멀티/커스텀 오케스트레이션 = `StateGraph`(직접 구성).**

## 언제 나누나?

- 도구가 ~10개를 넘어 라우팅 정확도가 떨어질 때
- 도메인별로 `system_prompt`/도구 세트를 분리하면 각자 더 정확할 때
- 단, 호출이 중첩되어 **토큰·지연이 늘어나므로** 분리가 분명히 이득일 때만.

## 관련 폴더

- [`../9.agentic_patterns/9.4_orchestrator_worker.py`](../9.agentic_patterns/) — 동적 작업 분해(StateGraph)
- [`../9.langgraph/`](../../9.langgraph/) — LangGraph 본격 학습 (StateGraph 기초부터)
- [`../7.routing/`](../7.routing/) — 단일 에이전트 안에서의 도구 라우팅
- 더 정교한 핸드오프/공유 상태 → `langgraph-supervisor`, LangGraph `StateGraph`
