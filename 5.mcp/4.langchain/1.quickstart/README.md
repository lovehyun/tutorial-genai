# 4.langchain/1.quickstart — `langchain-mcp-adapters` 로 5분 만에

MCP 서버의 도구를 **LangChain 에이전트가 자동으로 골라 쓰게** 만드는 가장 짧은 경로.
`2.langchain_agent/`가 "수동 변환"부터 보여주는 것과 달리, 여기는 어댑터가 변환을 대신 해주는
**가장 쉬운 진입점**이다 — `5.mcp/README.md`의 학습 단계표에서 2단계로 지목된 폴더가 이곳이다.

## 순서

| 파일 | 내용 |
|---|---|
| `1.agent.py` | 내가 만든 MCP 서버(`1.basic/2.protocol_deep/5.server_tools_resource.py`)를 에이전트에 연결 |
| `2.official_server.py` | 공식 filesystem MCP 서버(Node/npx)를 그대로 가져다 씀 — "한 번 만든 서버는 어디서든 재사용" |
| `3.mcp_plus_local.py` | 공식 MCP 도구 + 내 로컬 `@tool` 을 한 에이전트에 혼합 |
| `4.multi_server.py` | **`MultiServerMCPClient`로 여러 MCP 서버를 동시에** 연결(내 서버 + 공식 서버) |

## 실행
```bash
pip install mcp langchain-mcp-adapters langchain-openai langgraph
# .env 에 OPENAI_API_KEY
node --version    # 2번부터는 공식 filesystem 서버(Node/npx) 필요

python 1.agent.py             # 내 서버 → 에이전트가 자동 호출
python 2.official_server.py   # 공식 서버 → 코드 한 줄 안 바꿔도 재사용됨
python 3.mcp_plus_local.py    # MCP 도구 + 로컬 @tool 혼합
python 4.multi_server.py      # 서버 여러 개 동시 연결
```

## 관전 포인트
- `langchain-mcp-adapters`가 `list_tools()`로 발견한 MCP 도구를 LangChain `BaseTool`로
  **자동 변환**한다 — `2.langchain_agent/`가 손으로 하는 그 변환을 어댑터가 대신 해준다.
- `1.agent.py`와 `2.official_server.py`는 클라이언트 코드가 거의 동일하다. 서버가
  `python`(내 코드)이냐 `npx`(공식 서버)냐만 다르다 — MCP가 "서버 하나, 클라이언트 재사용"인
  것처럼 "클라이언트 코드도 서버 출처를 안 가린다"는 걸 보여준다.
- `4.multi_server.py`는 이름→서버설정 딕셔너리를 `MultiServerMCPClient`에 넘기면 모든 서버의
  도구가 하나의 리스트로 합쳐진다 — `2.openai/2.multi_tools/`와 같은 그림을 LangChain으로.

## 다음 단계
- 어댑터 없이 **손으로 변환**하는 법부터 보고 싶다면 → [`../2.langchain_agent/`](../2.langchain_agent/)
- 재사용 가능한 **브릿지 클래스**로 일반화 → [`../3.langchain_bridge/`](../3.langchain_bridge/)
- LLM 없이 순수 MCP 프로토콜만 먼저 보고 싶다면 → [`../../1.basic/`](../../1.basic/)
