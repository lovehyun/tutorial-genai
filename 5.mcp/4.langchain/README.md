# 4.langchain — LangChain 에서 MCP 서버 쓰기

MCP 서버의 도구를 **LangChain/LangGraph 에이전트**가 자동으로 발견·호출하게 만드는 법을
쉬운 것부터 심화까지 단계별로 본다. `1.basic/`이 LLM 없이 프로토콜 자체를 다뤘다면, 여기는
그 위에 LangChain 을 얹는다.

| 폴더 | 내용 |
|---|---|
| [`1.quickstart/`](1.quickstart/) | `langchain-mcp-adapters` 로 5분 만에 — **가장 쉬운 진입점** |
| [`2.langchain_agent/`](2.langchain_agent/) | 어댑터 없이 **손으로** MCP 도구 → LangChain `Tool` 변환 |
| [`3.langchain_bridge/`](3.langchain_bridge/) | 재사용 가능한 `MCPBridge` 클래스로 일반화, LangGraph 연결 |
| [`4.tools_safety/`](4.tools_safety/) | 프롬프트 가드레일로 에이전트의 도구 사용 범위 제한 |
| [`5.remote_http/`](5.remote_http/) | stdio → 원격 HTTP 서버, 실전 API(yfinance) 서버, 멀티서버 동시 연결 |
| [`6.human_in_loop/`](6.human_in_loop/) | 되돌릴 수 없는 도구 실행 전 **사람 승인** |
| [`7.guardrails/`](7.guardrails/) | **코드가 판정**하는 가드레일 — 인젝션·rm -rf·PII·악성 MCP 서버(tool poisoning) |
| `0.legacy(deprecated)/` | 옛 `create_react_agent`+`AgentExecutor`+`hub.pull` 문법 — 학습 히스토리 보존 |

## 추천 순서

```
1.quickstart → 2.langchain_agent → 3.langchain_bridge → 4.tools_safety
             → 5.remote_http → 6.human_in_loop → 7.guardrails
```

## 관전 포인트
- **`1.quickstart`가 지름길, `2.langchain_agent`가 원리**: 먼저 어댑터로 "이렇게 쉽다"를 보고,
  그다음 손으로 변환하며 "어댑터가 실제로 뭘 대신 해주는지"를 이해하는 순서를 권장한다.
- `7.guardrails`와 `2.langchain/11.guardrails`(레포 최상위)는 중복이 아니다 — 최상위 쪽은
  MCP 없이도 필요한 **일반 가드레일**, 여기는 **MCP 고유 문제**(도구 설명/스키마를 신뢰해도
  되는가 — tool poisoning, rug pull)에 집중한다. `7.guardrails/README.md`가 둘을 명시적으로 구분한다.
- 서버 코드는 순수 MCP(FastMCP)로만 작성된다 — **LangChain 은 항상 클라이언트 쪽에만** 있다.
  (`5.remote_http`가 이걸 "서버엔 LangChain 이 없다"고 직접 확인시켜준다.)

## 설치
```bash
pip install mcp langchain langchain-openai langchain-mcp-adapters langgraph
# .env 에 OPENAI_API_KEY
```

## 다음 단계
- LLM 없이 프로토콜 자체부터 → [`../1.basic/`](../1.basic/)
- GPT function calling 으로 직접(LangChain 없이) → [`../2.openai/`](../2.openai/)
- 실전 캡스톤 프로젝트 → [`../10.projects/`](../10.projects/)
