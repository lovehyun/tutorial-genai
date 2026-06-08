"""
MCP 4단계: 내 MCP 서버를 LangChain 에이전트에 연결한다.
이 예제: 1.common 의 toolbox 서버(3.server_tools_resource)를 띄우고, 그 도구들을 LLM 에이전트가 자동으로 골라 쓰게 한다.

순수 클라이언트(1.common/1.intro/4.hello_client)와의 차이:
  - 그건 우리가 직접 list_tools / call_tool 을 호출했다(수동).
  - 여기선 langchain-mcp-adapters 가 MCP 도구 → LangChain Tool 로 자동 변환하고,
    LLM 이 질문을 보고 '어떤 도구를 어떤 인자로' 부를지 스스로 결정한다(자동).

준비:
  pip install mcp langchain-mcp-adapters langchain-openai langgraph
  .env 에 OPENAI_API_KEY

흐름:
  1) MultiServerMCPClient 로 내 서버(3.server_tools_resource) 를 stdio 로 띄운다
  2) get_tools() 로 MCP 도구 → LangChain Tool 변환
  3) create_agent 에 넣으면 끝 — 일반 LangChain 도구와 똑같이 동작
"""

import asyncio
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
# 내가 1.common 에서 만든 서버를 그대로 재사용 (도구와 사용처의 분리)
SERVER = os.path.join(HERE, "..", "..", "1.common", "2.protocol_deep", "5.server_tools_resource.py")


async def main():
    # 1) 내 MCP 서버를 자식 프로세스로 띄운다 (2.official_server 의 공식 npx 서버와 형태가 같다)
    client = MultiServerMCPClient({
        "toolbox": {
            "command": "python",
            "args": [SERVER],
            "transport": "stdio",
        },
    })

    # 2) MCP 도구 → LangChain Tool 자동 변환
    tools = await client.get_tools()
    print(f"가져온 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    # 3) 에이전트 — 일반 도구처럼 사용
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = "12 더하기 30은 얼마야? 그리고 '오늘 날씨 정말 좋다' 는 몇 단어인지도 알려줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    # LLM 이 어떤 MCP 도구를 호출했는지 추적
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → MCP 도구 호출: {c['name']}({c['args']})")

    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

# 정리:
#   - 내가 1.common 에서 만든 서버를 그대로 에이전트가 사용 — '소유한 도구' 로 시작해 여기 도달.
#   - 서버 주소만 바꾸면(2.official_server) 공식 외부 서버도 똑같은 코드로 붙는다.
