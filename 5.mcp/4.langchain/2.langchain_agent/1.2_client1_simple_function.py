# 1.2_client1_simple_function.py
# MCP 도구를 @tool 비동기 함수로 감싸 create_agent 에 연결 (현행 LangChain 1.x).
# - 호출-단위(stateless)로 MCP stdio 세션을 열고 닫는다.
# - @tool async → 동기 func + asyncio.run() 중첩(RuntimeError) 회피.
#
# (옛 create_react_agent + AgentExecutor + hub.pull → 현행 create_agent.
#  옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/2.langchain_agent_react_hub.py)

import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()


@tool
async def say_hello(name: str) -> str:
    """이름을 입력받아 인사말을 생성합니다."""
    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("say_hello", {"name": name})
            if not result.content:
                return "빈 응답"
            return getattr(result.content[0], "text", str(result.content[0]))


async def main():
    print("간단한 MCP 클라이언트 (create_agent + @tool 비동기 함수)")

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    # 옛 create_react_agent(llm, tools, prompt) + AgentExecutor(...) + hub.pull → 아래 한 줄로 대체
    agent = create_agent(llm, [say_hello])

    for q in ["Alice에게 인사해줘", "Bob에게 Hello라고 말해줘"]:
        print(f"\n질문: {q}")
        result = await agent.ainvoke({"messages": [("user", q)]})
        print(f"결과: {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
