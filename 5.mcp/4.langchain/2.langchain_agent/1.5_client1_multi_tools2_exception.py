# 1.5_client1_multi_tools2_exception.py
# 1.4 확장 — 멀티툴 + 예외 처리 (현행 create_agent, server2.py).
# 공통 호출 헬퍼에서 예외를 잡아 '문자열'로 반환 → 한 도구가 실패해도 에이전트는 계속.
#
# (옛 create_react_agent + AgentExecutor + hub → create_agent. 비교: 0.legacy(deprecated)/)

import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

SERVER = "server2.py"


async def _call(tool_name: str, args: dict) -> str:
    """MCP 도구 호출 + 예외를 우아하게 문자열로 반환"""
    try:
        server_params = StdioServerParameters(command="python", args=[SERVER])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, args)
                return result.content[0].text if result.content else "빈 응답"
    except Exception as e:
        return f"'{tool_name}' 호출 오류: {e}"


@tool
async def say_hello(name: str) -> str:
    """사람 이름을 받아 인사말을 생성한다."""
    return await _call("say_hello", {"name": name})


@tool
async def add(a: int, b: int) -> str:
    """두 정수를 더한다."""
    return await _call("add", {"a": a, "b": b})


@tool
async def multiply(a: int, b: int) -> str:
    """두 정수를 곱한다."""
    return await _call("multiply", {"a": a, "b": b})


async def main():
    print("=" * 60)
    print("다중 도구 + 예외 처리 (create_agent)")
    print("=" * 60)

    tools = [say_hello, add, multiply]
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    agent = create_agent(llm, tools)

    queries = ["Bob에게 인사해줘", "50과 75를 더해줘", "9 곱하기 6은?"]
    for i, q in enumerate(queries, 1):
        print(f"\n[테스트 {i}] {q}")
        try:
            result = await agent.ainvoke({"messages": [("user", q)]})
            print(f"결과: {result['messages'][-1].content}")
        except Exception as e:
            print(f"실행 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
