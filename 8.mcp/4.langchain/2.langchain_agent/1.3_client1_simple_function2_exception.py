# 1.3_client1_simple_function2_exception.py
# 1.2 확장 — 도구 호출에 예외 처리를 더한다 (현행 create_agent + @tool 비동기 함수).
# 도구 내부에서 예외를 잡아 '문자열'로 반환 → 에이전트가 중단 없이 보고할 수 있다.
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


@tool
async def say_hello(name: str) -> str:
    """MCP 서버를 통해 인사말을 생성합니다. 입력: 사람 이름."""
    try:
        server_params = StdioServerParameters(command="python", args=["server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("say_hello", {"name": name})
                return result.content[0].text if result.content else "빈 응답"
    except Exception as e:
        return f"MCP 호출 에러: {e}"


async def main():
    print("=" * 60)
    print("간단한 함수 기반 방식 + 예외 처리 (create_agent)")
    print("=" * 60)

    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    agent = create_agent(llm, [say_hello])

    for i, q in enumerate(["Alice에게 인사해줘", "Bob에게 Hello라고 말해줘",
                           "Charlie에게 안녕하세요라고 인사해주세요"], 1):
        print(f"\n[테스트 {i}] {q}")
        try:
            result = await agent.ainvoke({"messages": [("user", q)]})
            print(f"결과: {result['messages'][-1].content}")
        except Exception as e:
            print(f"실행 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())
