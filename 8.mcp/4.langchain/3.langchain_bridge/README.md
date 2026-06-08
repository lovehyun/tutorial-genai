# 4.langchain/3.langchain_bridge — MCP ↔ LangChain / LangGraph 브릿지

`MCPBridge` 라는 재사용 클래스로 MCP 서버의 도구를 자동 발견·변환하고,
LangChain ReAct 에이전트와 LangGraph 에이전트에 각각 연결한다.
(2.langchain_agent 의 '수동 변환'을 한 클래스로 일반화한 형태.)

## 파일
- `server.py` — say_hello·add·multiply·now·square_root·factorial (6개)
- `mcp_bridge.py` — 핵심: 도구 발견 → 입력 파싱 → LangChain `Tool` 생성
- `mcp_bridge2_except.py` — 예외 처리 + 유틸(test_connection / get_tool_info 등) 보강
- `2.langchain_agent_demo.py` — `SimpleMCPAgent`(브릿지) + `create_agent`
- `2.langchain_agent2_demo_except.py` — `create_agent` + 예외 처리 + 스트리밍(`astream`)
- `3.langgraph_agent_demo.py` — `create_agent` (system_prompt 지정)
- `4.langgraph_agent2_demo_except.py` — `create_agent` + 스트리밍/디버그
- `requirements.txt` — 의존성 모음

> **현행 API 주의**: 옛날엔 ReAct(`AgentExecutor`)와 LangGraph(`langgraph.prebuilt.create_react_agent`)
> 두 갈래였지만, **LangChain 1.x 에선 `langchain.agents.create_agent` 하나로 통합**됐습니다
> (create_agent 자체가 LangGraph 그래프). 옛 문법은 [`../0.legacy(deprecated)/`](../0.legacy(deprecated)/) 참고.

## 실행
```bash
cd 8.mcp/4.langchain/3.langchain_bridge
pip install -r requirements.txt        # langchain · langgraph · mcp · openai 등
# .env 에 OPENAI_API_KEY

python 2.langchain_agent_demo.py       # 메뉴: 자동 데모 / 대화형
python 3.langgraph_agent_demo.py
python 4.langgraph_agent2_demo_except.py   # 스트리밍 / 디버그 모드
```
> 브릿지가 `server.py` 를 stdio 로 **자동 실행**. 폴더 안에서 실행.

## 관전 포인트
- **브릿지 패턴**: MCP↔LangChain 변환 로직을 한 클래스로 묶어 재사용 — 2.langchain_agent 의 수동 변환을 추상화.
- **1·2 vs 3·4**: 같은 `create_agent` 를 기본/예외·스트리밍(2), system_prompt(3), 스트리밍·디버그(4) 로 활용하는 차이.
- 같은 `server.py` 를 모든 데모가 그대로 쓴다 → 서버 무관성.
- (참고) 더 간단한 길은 `1.quickstart` 의 `MultiServerMCPClient.get_tools()` — 이 브릿지는 "어댑터가 내부에서 무엇을 하는지" 를 손으로 보여주는 학습용.

## 추천 순서
`mcp_bridge` 이해 → `1.langchain` → `2.modern` → `3.langgraph` → `4.langgraph2`
