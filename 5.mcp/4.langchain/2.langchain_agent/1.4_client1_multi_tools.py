# 1.4_client1_multi_tools.py
# 여러 MCP 도구를 @tool 비동기 함수로 감싸 멀티툴 에이전트 구성 (현행 create_agent, server2.py).
# 새 도구 추가 = "@tool 비동기 함수 하나 + tools 리스트에 추가" 만 하면 끝.
#
# (옛 create_react_agent + AgentExecutor + hub → create_agent. 비교: 0.legacy(deprecated)/)
# 개선점: 단일-문자열 Tool(func) → 타입 인자를 받는 @tool 비동기 함수(StructuredTool) 로,
#         server.py(say_hello 1개) → server2.py(say_hello/add/multiply/get_day_of_week) 로.

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
    """server2.py 에 연결해 MCP 도구 하나를 호출하고 텍스트 결과 반환 (호출-단위 연결)"""
    server_params = StdioServerParameters(command="python", args=[SERVER])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            return result.content[0].text if result.content else "빈 응답"


# ─── MCP 도구들을 @tool 비동기 함수로 감싼다 (타입힌트+docstring 이 곧 LLM 명세) ───
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


@tool
async def get_day_of_week() -> str:
    """오늘이 무슨 요일인지 알려준다."""
    return await _call("get_day_of_week", {})


async def main():
    print("다중 도구 확장 방식 MCP 클라이언트 (create_agent)")
    print("=" * 50)

    tools = [say_hello, add, multiply, get_day_of_week]
    print(f"등록된 도구 {len(tools)}개:", [t.name for t in tools])

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    agent = create_agent(llm, tools)   # 도구 리스트만 넘기면 LLM 이 알아서 라우팅

    queries = ["Alice에게 인사해줘", "10과 20을 더해줘", "7 곱하기 8은?", "오늘 무슨 요일이야?"]
    for i, q in enumerate(queries, 1):
        print(f"\n[테스트 {i}] {q}")
        result = await agent.ainvoke({"messages": [("user", q)]})
        for m in result["messages"]:
            for c in getattr(m, "tool_calls", []) or []:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
        print(f"결과: {result['messages'][-1].content}")

    print("\n확장 방법: @tool 비동기 함수 하나 추가 → tools 리스트에 넣기. 끝.")


if __name__ == "__main__":
    asyncio.run(main())
