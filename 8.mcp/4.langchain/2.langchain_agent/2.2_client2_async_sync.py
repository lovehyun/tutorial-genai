# 2.2_client2_async_sync.py
# 동기(.invoke) vs 비동기(.ainvoke) — MCP 처럼 async I/O 도구는 .ainvoke() 가 자연스럽다 (현행 create_agent).
#
# 옛 방식의 문제: 동기 Tool(func) 내부에서 asyncio.run() → 이미 실행 중인 루프 안에서 호출되면
#   RuntimeError: asyncio.run() cannot be called from a running event loop.
# 현행 해결: @tool async + agent.ainvoke() → 하나의 이벤트 루프에서 await (중첩 없음).
# (옛 문법 비교: 8.mcp/4.langchain/0.legacy(deprecated)/2.langchain_agent_react_prompttemplate.py)

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
    server_params = StdioServerParameters(command="python", args=[SERVER])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, args)
            return result.content[0].text if result.content else "빈 응답"


@tool
async def say_hello(name: str) -> str:
    """사람 이름을 받아 인사말을 생성한다."""
    return await _call("say_hello", {"name": name})


@tool
async def add(a: int, b: int) -> str:
    """두 정수를 더한다."""
    return await _call("add", {"a": a, "b": b})


def build_agent():
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    return create_agent(llm, [say_hello, add])


# ─── 비동기 경로 (권장) — 하나의 루프에서 await ───────────────
async def run_async():
    print("[비동기] agent.ainvoke() — MCP async 도구에 자연스러운 경로")
    agent = build_agent()
    for q in ["Charlie에게 인사해주세요", "50과 75를 더해주세요"]:
        result = await agent.ainvoke({"messages": [("user", q)]})
        print(f"  {q} → {result['messages'][-1].content}")


# ─── 동기 경로 — 동기 코드에서 async 에이전트를 쓰려면 최상위에서 asyncio.run 으로 감싼다 ───
def run_sync():
    print("[동기] 최상위에서 asyncio.run(agent.ainvoke(...)) 로 감싸 호출")
    agent = build_agent()
    for q in ["Alice에게 인사해줘", "10과 25를 더해주세요"]:
        # 중요: 실행 중인 루프가 없는 최상위에서만 asyncio.run 안전 (루프 중첩 금지)
        result = asyncio.run(agent.ainvoke({"messages": [("user", q)]}))
        print(f"  {q} → {result['messages'][-1].content}")


if __name__ == "__main__":
    print("MCP 도구는 async I/O — 권장은 .ainvoke()")
    print("1) 동기(최상위 asyncio.run)   2) 비동기(권장)")
    choice = input("선택 (1 또는 2, 기본 2): ").strip()
    if choice == "1":
        run_sync()
    else:
        asyncio.run(run_async())

# 정리:
#   - @tool async + agent.ainvoke() = 권장 (서버/노트북 등 루프가 이미 도는 환경에서도 안전)
#   - 동기 코드에서 쓰려면 최상위 1회만 asyncio.run() 으로 감싼다 (절대 루프 안에서 asyncio.run 금지)
