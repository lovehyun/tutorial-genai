# pip install mcp langchain-mcp-adapters langchain-openai langgraph python-dotenv
#
# LangChain 이 **같은 server.py**를 세 번째로 재사용한다. langchain-mcp-adapters 가 변환을
# 대신 해줘서 1.client_openai.py / 2.client_anthropic.py 처럼 스키마 변환 함수를 직접 안 짜도 된다
# — 그 변환기 자체가 "MCP 도구를 벤더별 형식으로 바꾸는 어댑터"라는 걸 앞의 두 파일로 먼저 보고 오면
# 여기서 어댑터가 뭘 대신 해주는지 더 잘 보인다.

import asyncio

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()


async def main():
    client = MultiServerMCPClient({
        "toolbox": {"command": "python", "args": ["server.py"], "transport": "stdio"},
    })
    tools = await client.get_tools()
    print("[LangChain] 가져온 도구:", [t.name for t in tools])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    for question in ["서울 날씨 어때?", "23 곱하기 7은?"]:
        print(f"\n[LangChain] 질문: {question}")
        result = await agent.ainvoke({"messages": [("user", question)]})
        for m in result["messages"]:
            if hasattr(m, "tool_calls") and m.tool_calls:
                for c in m.tool_calls:
                    print(f"[LangChain] 도구 호출: {c['name']}({c['args']})")
        print(f"[LangChain] 답: {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
