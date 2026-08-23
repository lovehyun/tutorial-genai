# pip install mcp anthropic python-dotenv
#
# Claude(Anthropic API)가 **같은 server.py**를 자동 선택·호출한다. 1.client_openai.py 와 서버는
# 완전히 동일 — 바뀌는 건 "MCP 도구 스키마를 어느 벤더 형식으로 변환하는가"와 tool_use 프로토콜뿐.
# Anthropic 은 스키마 필드명이 input_schema(snake_case) — MCP 의 inputSchema(camelCase) 와 다르다.

import asyncio
import os

import anthropic
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def to_anthropic_tools(mcp_tools):
    """MCP 도구 스키마(inputSchema) → Anthropic tool_use 형식(input_schema)."""
    return [{
        "name": t.name, "description": t.description, "input_schema": t.inputSchema,
    } for t in mcp_tools]


async def ask(session, an_tools, question):
    print(f"\n[Anthropic] 질문: {question}")
    messages = [{"role": "user", "content": question}]

    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)

    if resp.stop_reason != "tool_use":
        print(f"[Anthropic] 답: {next(b.text for b in resp.content if b.type == 'text')}")
        return

    messages.append({"role": "assistant", "content": resp.content})
    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            print(f"[Anthropic] 도구 호출: {block.name}({block.input})")
            # MCP 서버에서 실행 — 도구 구현은 여기 없다, 서버가 갖고 있다.
            result = await session.call_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result.content[0].text,
            })
    messages.append({"role": "user", "content": tool_results})

    final = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)
    print(f"[Anthropic] 답: {next(b.text for b in final.content if b.type == 'text')}")


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            an_tools = to_anthropic_tools(tools)

            await ask(session, an_tools, "서울 날씨 어때?")
            await ask(session, an_tools, "23 곱하기 7은?")


if __name__ == "__main__":
    asyncio.run(main())
