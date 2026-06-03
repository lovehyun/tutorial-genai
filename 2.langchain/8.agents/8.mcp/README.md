# 8.mcp → 최상위 [`/8.mcp`](../../../8.mcp/) 로 이전되었습니다

MCP(Model Context Protocol)는 특정 프레임워크에 묶이지 않는 **provider 중립 주제**이고
분량이 커서, LangChain 에이전트 폴더 안에 두기보다 **레포 최상위 [`8.mcp/`](../../../8.mcp/)** 로 승격했습니다.

## 어디로 갔나요

| 찾는 내용 | 새 위치 |
|-----------|---------|
| MCP 가 뭔지 / 내 서버 만들기 / 순수 클라이언트 / 전송(stdio·HTTP) | [`/8.mcp/1.common/`](../../../8.mcp/1.common/) |
| GPT(OpenAI)로 MCP 도구 호출 | [`/8.mcp/2.openai/`](../../../8.mcp/2.openai/) |
| Claude API · Claude Desktop 연동 | [`/8.mcp/3.anthropic/`](../../../8.mcp/3.anthropic/) |
| **LangChain 에이전트에서 MCP 쓰기** | [`/8.mcp/4.langchain/`](../../../8.mcp/4.langchain/) |
| VSCode 연동 | [`/8.mcp/5.vscode/`](../../../8.mcp/5.vscode/) |
| 실전 프로젝트 | [`/8.mcp/9.projects/`](../../../8.mcp/9.projects/) |

## LangChain 학습자라면

이 폴더(`2.langchain/8.agents`)에서 에이전트를 익힌 뒤, MCP 연동은 곧장
**[`/8.mcp/4.langchain/0.quickstart/`](../../../8.mcp/4.langchain/0.quickstart/)** 로 가세요.
`langchain-mcp-adapters` 로 MCP 서버 도구를 에이전트에 붙이는 빠른 시작이 거기에 있습니다.

```python
# 핵심 패턴 (자세한 실행 코드는 /8.mcp/4.langchain/0.quickstart/1.agent.py)
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient({
    "toolbox": {"command": "python", "args": ["<MCP 서버.py>"], "transport": "stdio"},
})
tools = await client.get_tools()          # MCP 도구 → LangChain Tool 자동 변환
agent = create_agent(llm, tools)
```
