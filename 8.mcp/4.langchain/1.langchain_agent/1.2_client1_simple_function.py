# 1.2_client1_simple_function.py
# - LangChain Tool을 비동기 coroutine으로 등록 (asyncio.run() 사용 금지)
# - 호출-단위(stateless)로 MCP stdio 세션 열고 닫기

import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_core.tools import Tool

load_dotenv()


async def call_say_hello_async(name: str) -> str:
    """server.py의 say_hello MCP 도구 호출 (비동기, 호출-단위 연결)"""
    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("say_hello", {"name": name})
            if not result.content:
                return "빈 응답"
            item = result.content[0]
            return getattr(item, "text", str(item))


def create_mcp_tool() -> Tool:
    """비동기 Tool 등록: coroutine 파라미터 필수"""
    return Tool(
        name="say_hello",
        description="이름을 입력받아 인사말을 생성합니다",
        coroutine=call_say_hello_async,
    )


async def main():
    print("간단한 MCP 클라이언트 실행 (비동기 Tool)")

    tool = create_mcp_tool()
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    # 프롬프트: hub.pull 실패 시 로컬 텍스트로 폴백
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        prompt = """You are a helpful ReAct agent.
Use the tool when you need to greet someone by name.
Format:
Thought: ...
Action: say_hello
Action Input: <name>
Observation: ...
... (repeat)
Final Answer: <final>"""

    agent = create_react_agent(llm, [tool], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)

    queries = ["Alice에게 인사해줘", "Bob에게 Hello라고 말해줘"]
    for q in queries:
        print(f"\n질문: {q}")
        resp = await agent_executor.ainvoke({"input": q})
        print(f"결과: {resp.get('output')}")


if __name__ == "__main__":
    asyncio.run(main())
