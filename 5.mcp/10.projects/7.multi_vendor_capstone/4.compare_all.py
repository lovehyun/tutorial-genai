# pip install mcp openai anthropic langchain-mcp-adapters langchain-openai langgraph python-dotenv
#
# 이 캡스톤의 결론 파일 — 같은 질문을 세 벤더에게 동시에 던지고, 다들 **같은 server.py**를 통해
# 답한다는 걸 한 화면에서 확인한다. 1~3번이 "벤더 하나씩" 이었다면 여기는 "셋을 나란히".
# 서버 프로세스는 벤더마다 별도로(stdio 세션은 1:1) 띄우지만, server.py 코드는 단 한 벌이다.

import asyncio
import json

from dotenv import load_dotenv
from openai import AsyncOpenAI
import anthropic
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()
openai_client = AsyncOpenAI()
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SERVER = StdioServerParameters(command="python", args=["server.py"])


async def ask_openai(question: str) -> str:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            oa_tools = [{"type": "function", "function": {
                "name": t.name, "description": t.description, "parameters": t.inputSchema,
            }} for t in tools]

            r = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}],
                tools=oa_tools, tool_choice="auto",
            )
            msg = r.choices[0].message
            if not msg.tool_calls:
                return msg.content
            call = msg.tool_calls[0]
            args = json.loads(call.function.arguments)
            result = await session.call_tool(call.function.name, args)
            r2 = await openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": question}, msg,
                    {"role": "tool", "tool_call_id": call.id, "content": result.content[0].text},
                ],
            )
            return r2.choices[0].message.content


async def ask_anthropic(question: str) -> str:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            an_tools = [{"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                        for t in tools]

            messages = [{"role": "user", "content": question}]
            resp = anthropic_client.messages.create(
                model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)
            if resp.stop_reason != "tool_use":
                return next(b.text for b in resp.content if b.type == "text")

            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    result = await session.call_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result", "tool_use_id": block.id,
                        "content": result.content[0].text,
                    })
            messages.append({"role": "user", "content": tool_results})
            final = anthropic_client.messages.create(
                model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)
            return next(b.text for b in final.content if b.type == "text")


async def ask_langchain(question: str) -> str:
    client = MultiServerMCPClient({
        "toolbox": {"command": "python", "args": ["server.py"], "transport": "stdio"},
    })
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)
    result = await agent.ainvoke({"messages": [("user", question)]})
    return result["messages"][-1].content


async def compare(question: str):
    print(f"\n{'=' * 60}\n질문: {question}\n{'=' * 60}")

    # [관전 포인트] 세 벤더를 동시에(asyncio.gather) 실행 — 서버 프로세스는 3개 뜨지만
    #   server.py 코드는 한 벌뿐이다. "서버 하나, 클라이언트 벤더 수만큼"을 시간까지 아껴 보여준다.
    openai_answer, anthropic_answer, langchain_answer = await asyncio.gather(
        ask_openai(question), ask_anthropic(question), ask_langchain(question),
    )
    print(f"[OpenAI]     {openai_answer}")
    print(f"[Anthropic]  {anthropic_answer}")
    print(f"[LangChain]  {langchain_answer}")


async def main():
    for q in ["서울 날씨 어때?", "23 곱하기 7은?"]:
        await compare(q)


if __name__ == "__main__":
    asyncio.run(main())
