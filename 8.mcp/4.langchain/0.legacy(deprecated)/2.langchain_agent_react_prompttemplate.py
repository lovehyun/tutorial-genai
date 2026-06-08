# ⚠️ DEPRECATED (보존용) — 원본: 4.langchain/2.langchain_agent/2.2_client2_async_sync.py
# 옛 LangChain 0.x 문법 박제. langchain 1.x 에서는 import 실패.
#
# ─── 무엇이 무엇으로 바뀌었나 ────────────────────────────────────────────────
#   create_react_agent + AgentExecutor + PromptTemplate(수동 ReAct 프롬프트)
#       → create_agent(llm, tools)  (프롬프트 스캐폴딩 전부 불필요)
#   Tool(func=동기함수) + 내부 asyncio.run()  → 중첩 이벤트 루프(RuntimeError) 위험
#       → Tool(coroutine=비동기함수) + agent.ainvoke(...)
#   executor.invoke({"input": q})["output"]  → agent.invoke({"messages":[("user",q)]})["messages"][-1].content
# 현행 버전: 4.langchain/2.langchain_agent/2.2_client2_async_sync.py (개선됨)
# ────────────────────────────────────────────────────────────────────────────

import asyncio
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor   # ← DEPRECATED
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate                # ← 옛 ReAct 프롬프트용

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

# 옛 방식: hub 없이 직접 ReAct 텍스트 프롬프트를 작성해서 넘김
REACT_PROMPT = """Answer the following questions as best you can. You have access to the following tools:
{tools}
Use the following format:
Question: the input question
Thought: you should always think about what to do
Action: one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat)
Final Answer: the final answer
Begin!
Question: {input}
Thought:{agent_scratchpad}"""


def call_mcp_hello(name: str) -> str:
    """동기 Tool — 내부에서 asyncio.run() (실행 중 루프 안에서 호출되면 RuntimeError)"""
    async def run():
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("say_hello", {"name": name})
                return result.content[0].text
    return asyncio.run(run())   # ← 중첩 이벤트 루프 위험 (현행은 coroutine= 사용)


def create_agent_executor():
    tools = [Tool(name="say_hello", func=call_mcp_hello, description="이름을 받아 인사말 생성")]
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
    prompt = PromptTemplate.from_template(REACT_PROMPT)
    agent = create_react_agent(llm, tools, prompt)              # ← DEPRECATED
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)  # ← DEPRECATED


def main():
    executor = create_agent_executor()
    for q in ["Alice에게 인사해줘", "Bob에게 안녕하세요 라고 말해줘"]:
        resp = executor.invoke({"input": q})                   # ← 옛 입력/출력 형식
        print(f"[결과] {resp['output']}")


if __name__ == "__main__":
    main()
