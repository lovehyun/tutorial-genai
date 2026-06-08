# 3.client_gpt.py — GPT(OpenAI function calling)가 MCP 도구를 '자동' 선택·호출
#
# ── 연동 방식 ────────────────────────────────────────────────
#   1) session.list_tools() 로 MCP 도구 발견
#   2) 그 스키마(inputSchema)를 OpenAI function calling 형식으로 변환 → to_openai()
#   3) GPT 에 tools=... , tool_choice="auto" 로 넘기면 GPT 가 '어떤 도구를 어떤 인자로' 결정
#   4) GPT 가 고른 도구를 session.call_tool() 로 MCP 실행
#   5) 실행 결과를 tool 메시지로 되돌려주면 GPT 가 자연스러운 문장으로 정리
#   (1.client_demo=수동 하드코딩, 2.client_simple_nlp=키워드, 여기=LLM 자동)

import asyncio
import json
import os
from dotenv import load_dotenv
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
gpt = openai.AsyncOpenAI()


def to_openai(tools):
    """MCP 도구 스키마 → OpenAI function calling 형식 (inputSchema 를 그대로 parameters 로)"""
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema,
    }} for t in tools]


async def ask(session, oa_tools, user_input):
    print(f"\n사용자: {user_input}")
    # 1) GPT 가 도구를 고르게 한다
    r = await gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}],
        tools=oa_tools, tool_choice="auto",
    )
    msg = r.choices[0].message
    if not msg.tool_calls:
        print(f"AI: {msg.content}")               # 도구 불필요 → 바로 답
        return

    # 2) GPT 가 고른 도구를 MCP 로 실행
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    print(f"  선택된 도구: {call.function.name}({args})")
    result = await session.call_tool(call.function.name, args)

    # 3) 실행 결과를 GPT 가 자연스럽게 정리 (tool 메시지로 되돌려줌 — 정석 패턴)
    r2 = await gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": user_input},
            msg,
            {"role": "tool", "tool_call_id": call.id, "content": result.content[0].text},
        ],
    )
    print(f"AI: {r2.choices[0].message.content}")


async def main():
    params = StdioServerParameters(command="python", args=["server2.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])
            oa_tools = to_openai(tools)
            for q in ["5 더하기 3은?", "지금 몇 시야?", "15 곱하기 7은?", "오늘 날씨는?"]:
                await ask(session, oa_tools, q)


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now', 'multiply', ...]
#   사용자: 5 더하기 3은?
#     선택된 도구: add({'a': 5, 'b': 3})
#   AI: 5 더하기 3은 8입니다.
#   사용자: 오늘 날씨는?          ← 맞는 도구가 없으면 GPT 가 도구 없이 바로 답
#   AI: 죄송하지만 현재 날씨 정보는 제공할 수 없습니다 ...
