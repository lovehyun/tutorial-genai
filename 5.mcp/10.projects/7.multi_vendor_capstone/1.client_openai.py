# pip install mcp openai python-dotenv
#
# OpenAI(GPT)가 server.py 의 도구를 자동 선택·호출한다. 패턴은 2.openai/1.agent_tool/3.client_gpt.py
# 와 동일하다 — 이 캡스톤의 요점은 "새로운 기법"이 아니라 "같은 서버를 다른 벤더가 그대로 쓴다"는 것.

import asyncio
import json

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = AsyncOpenAI()


def to_openai_tools(mcp_tools):
    """MCP 도구 스키마(inputSchema, camelCase) → OpenAI function calling 형식."""
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema,
    }} for t in mcp_tools]


async def ask(session, oa_tools, question):
    print(f"\n[OpenAI] 질문: {question}")

    r = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
        tools=oa_tools, tool_choice="auto",
    )
    msg = r.choices[0].message
    if not msg.tool_calls:
        print(f"[OpenAI] 답: {msg.content}")
        return

    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    print(f"[OpenAI] 도구 호출: {call.function.name}({args})")
    result = await session.call_tool(call.function.name, args)

    r2 = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": question},
            msg,
            {"role": "tool", "tool_call_id": call.id, "content": result.content[0].text},
        ],
    )
    print(f"[OpenAI] 답: {r2.choices[0].message.content}")


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            oa_tools = to_openai_tools(tools)

            await ask(session, oa_tools, "서울 날씨 어때?")
            await ask(session, oa_tools, "23 곱하기 7은?")


if __name__ == "__main__":
    asyncio.run(main())
