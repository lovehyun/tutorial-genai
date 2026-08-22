# ⚠️ DEPRECATED (보존용) — 원본: 4.langchain/2.langchain_agent/1.2_client1_simple_function.py
# 이 파일은 옛 LangChain 0.x 문법을 박제한 것입니다. langchain 1.x 에서는 import 자체가 실패합니다.
#
# ─── 무엇이 무엇으로 바뀌었나 ────────────────────────────────────────────────
#   from langchain.agents import create_react_agent, AgentExecutor   →  from langchain.agents import create_agent
#   from langchain import hub ; prompt = hub.pull("hwchase17/react")  →  (불필요 — 삭제)
#   agent = create_react_agent(llm, [tool], prompt)                   →  agent = create_agent(llm, [tool])
#   executor = AgentExecutor(agent=agent, tools=[tool], verbose=True) →  (불필요 — create_agent 가 루프 포함)
#   await executor.ainvoke({"input": q}) ; resp["output"]            →  await agent.ainvoke({"messages":[("user", q)]}) ; result["messages"][-1].content
#   Tool(func=동기함수)+내부 asyncio.run()                            →  Tool(coroutine=비동기함수)
# 현행 버전: 4.langchain/2.langchain_agent/1.2_client1_simple_function.py (개선됨)
# ────────────────────────────────────────────────────────────────────────────

# 1.2_client1_simple_function.py
# - LangChain Tool을 비동기 coroutine으로 등록 (asyncio.run() 사용 금지)
# - 호출-단위(stateless)로 MCP stdio 세션 열고 닫기

import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor   # ← DEPRECATED (1.x 에서 제거됨)
from langchain import hub                                        # ← DEPRECATED
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
    return Tool(
        name="say_hello",
        description="이름을 입력받아 인사말을 생성합니다",
        coroutine=call_say_hello_async,
    )


async def main():
    tool = create_mcp_tool()
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    # ↓ 옛 방식: hub 에서 ReAct 텍스트 프롬프트를 받아 와 create_react_agent + AgentExecutor 로 감쌈
    try:
        prompt = hub.pull("hwchase17/react")
    except Exception:
        prompt = "You are a helpful ReAct agent.\nThought/Action/Action Input/Observation/Final Answer 형식 사용."

    agent = create_react_agent(llm, [tool], prompt)              # ← DEPRECATED
    agent_executor = AgentExecutor(agent=agent, tools=[tool], verbose=True)  # ← DEPRECATED

    for q in ["Alice에게 인사해줘", "Bob에게 Hello라고 말해줘"]:
        print(f"\n질문: {q}")
        resp = await agent_executor.ainvoke({"input": q})        # ← 옛 입력/출력 형식
        print(f"결과: {resp.get('output')}")


if __name__ == "__main__":
    asyncio.run(main())
