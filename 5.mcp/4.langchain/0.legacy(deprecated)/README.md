# 0.legacy(deprecated) — 옛 LangChain 에이전트 문법 (참고 보존용)

이 폴더는 **더 이상 쓰지 않는 옛 문법**을 "무엇이 무엇으로 바뀌었는지" 비교용으로 보존합니다.
실제 실습 코드는 모두 현행 API 로 개선되어 있고, 여기 파일들은 **대표 샘플 몇 개만** 남겨둔 것입니다.

> ⚠️ 이 폴더의 코드는 **langchain 1.x 에서 import 자체가 실패**합니다 (의도된 것 — 옛 문법 박제).
> 새 코드에는 절대 쓰지 마세요. 마이그레이션 시 "옛날엔 이랬다" 를 확인하는 용도입니다.

## 무엇이 무엇으로 바뀌었나 (핵심 매핑)

| 옛 문법 (deprecated, ~LangChain 0.x) | 현행 (LangChain 1.x) |
|---|---|
| `from langchain.agents import create_react_agent, AgentExecutor` | `from langchain.agents import create_agent` |
| `from langchain import hub` → `hub.pull("hwchase17/react")` | **불필요** (프롬프트 템플릿 스캐폴딩 제거) |
| `from langchain_core.prompts import PromptTemplate` + 수동 ReAct 프롬프트 | **불필요** |
| `agent = create_react_agent(llm, tools, prompt)` | `agent = create_agent(llm, tools)` |
| `executor = AgentExecutor(agent=agent, tools=tools, verbose=True)` | **불필요** (create_agent 가 그래프로 루프까지 포함) |
| `executor.invoke({"input": q})` | `agent.invoke({"messages": [("user", q)]})` |
| `await executor.ainvoke({"input": q})` | `await agent.ainvoke({"messages": [("user", q)]})` |
| `resp["output"]` | `result["messages"][-1].content` |
| `Tool(name=, func=동기함수)` + 내부 `asyncio.run()` | `Tool(name=, coroutine=비동기함수)` (중첩 이벤트 루프 방지) |

> 참고: 옛 `create_react_agent` 는 **텍스트 기반 ReAct**(Thought/Action/Observation 문자열 파싱)였고,
> 현행 `create_agent` 는 **LangGraph 그래프 + tool-calling** 기반이라 프롬프트 스캐폴딩이 필요 없습니다.
> (옛 `langgraph.prebuilt.create_react_agent` 도 `langchain.agents.create_agent` 로 이동·대체됨.)

## 보존된 대표 파일

| 파일 | 원본 위치 | 보여주는 옛 문법 |
|---|---|---|
| `2.langchain_agent_react_hub.py` | `4.langchain/2.langchain_agent/1.2_*` | `create_react_agent` + `AgentExecutor` + `hub.pull` |
| `2.langchain_agent_react_prompttemplate.py` | `4.langchain/2.langchain_agent/2.2_*` | `create_react_agent` + `AgentExecutor` + 수동 `PromptTemplate` |

→ 현행으로 고친 실제 코드: [`../4.langchain/`](../4.langchain/) (`1.quickstart` 가 기준 템플릿)
