"""
mcp-math 원격 클라이언트 — 이미 떠 있는 2c.mcp_math_remote_server.py 에 LangChain 에이전트를 붙인다.

2b.mcp_math_local_client.py 와의 차이 — 딱 설정 딕셔너리 한 덩어리뿐:
    stdio : {"command": "python", "args": [SERVER], "transport": "stdio"}      ← 서버를 내가 띄움
    http  : {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable_http"} ← 이미 떠 있는 서버에 접속
  get_tools() 이후의 코드(도구 변환 → create_agent → ainvoke)는 완전히 동일하다.

실행:
  터미널 1)  python 2c.mcp_math_remote_server.py   ← 먼저 서버를 띄워둔다(TODO 완료 후)
  터미널 2)  python 2d.mcp_math_remote_client.py
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    # TODO: 원격 서버에 접속하는 설정을 완성하세요.
    #   힌트 — stdio 였다면 {"command": ..., "args": ..., "transport": "stdio"} 였을 자리에,
    #     이번엔 이미 떠 있는 서버 URL 로 "접속"하는 설정을 넣는다.
    #   ⚠️ transport 리터럴이 서버 쪽과 다르다:
    #        서버   mcp.run(transport="streamable-http")   ← 하이픈
    #        클라   여기서는 언더스코어를 쓴다
    client = MultiServerMCPClient({
        "toolbox": {
            "url": None,        # ← SERVER_URL 을 채우세요
            "transport": None,  # ← "streamable_http" (언더스코어) 를 채우세요
        },
    })

    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"[연결 실패] {SERVER_URL} 에 붙지 못했습니다: {type(e).__name__}: {e}")
        print("→ 다른 터미널에서 'python 2c.mcp_math_remote_server.py' 를 먼저 실행했는지 확인하세요.")
        return

    print(f"원격 서버에서 가져온 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = "17 더하기 25는 얼마야? 그리고 '원격 MCP 서버에 붙었다' 가 몇 단어인지도 세줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 원격 도구 호출: {c['name']}({c['args']})")

    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
