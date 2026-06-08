# 3.client_gpt2_tryexcept.py — 3.client_gpt + 예외 처리 (실행 견고화)
# GPT function calling 으로 MCP 도구 자동 호출 + 각 단계(연결/선택/실행)에 try/except.

import asyncio
import json
from dotenv import load_dotenv
import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
gpt = openai.AsyncOpenAI()


def to_openai(tools):
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]


async def ask(session, oa_tools, user_input):
    print(f"\n사용자: {user_input}")
    try:
        r = await gpt.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_input}],
            tools=oa_tools, tool_choice="auto",
        )
        msg = r.choices[0].message
        if not msg.tool_calls:
            print(f"AI: {msg.content}")
            return
        call = msg.tool_calls[0]
        args = json.loads(call.function.arguments)
        print(f"  선택된 도구: {call.function.name}({args})")
        try:
            result = await session.call_tool(call.function.name, args)
            text = result.content[0].text
        except Exception as e:
            text = f"(도구 실행 실패: {e})"
        r2 = await gpt.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_input}, msg,
                {"role": "tool", "tool_call_id": call.id, "content": text},
            ],
        )
        print(f"AI: {r2.choices[0].message.content}")
    except Exception as e:
        print(f"AI: (처리 오류) {e}")


async def main():
    params = StdioServerParameters(command="python", args=["server2.py"])
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                print("도구:", [t.name for t in tools])
                oa_tools = to_openai(tools)
                for q in ["5 더하기 3은?", "지금 몇 시야?", "15 곱하기 7은?", "오늘 날씨는?"]:
                    await ask(session, oa_tools, q)
    except Exception as e:
        print(f"서버 연결 실패: {e} — server2.py 가 같은 폴더에 있는지 확인")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now', 'multiply', ...]
#   사용자: 5 더하기 3은?
#     선택된 도구: add({'a': 5, 'b': 3})
#   AI: 5 더하기 3은 8입니다.
#   (도구 실행이 실패하면 "(도구 실행 실패: ...)" 를 GPT 에 돌려줘 사용자에게 안내)
