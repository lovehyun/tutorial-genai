# 2.smart_client_gpt.py — GPT function calling 으로 '여러 MCP 서버'의 도구를 자동 선택·호출
# math_server + utility_server 의 도구를 한데 모아 OpenAI 에 넘기고,
# GPT 가 고른 도구를 '그 도구를 가진 서버 세션' 으로 실행한다.
# (1.smart_client_manual = 키워드 규칙 / 여기 = LLM 자동)

import json
import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
gpt = AsyncOpenAI()
SERVERS = ["math_server.py", "utility_server.py"]


async def connect(server_file, stack):
    """서버를 띄워 세션을 ExitStack 에 등록(수명 유지)하고 도구 목록 반환."""
    read, write = await stack.enter_async_context(
        stdio_client(StdioServerParameters(command="python", args=[server_file]))
    )
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session, (await session.list_tools()).tools


async def main():
    async with AsyncExitStack() as stack:
        oa_tools = []                 # OpenAI function 형식 도구 목록 (모든 서버 합본)
        tool_session = {}             # tool_name → 그 도구를 가진 세션 (실행 라우팅용)

        for sf in SERVERS:
            session, tools = await connect(sf, stack)
            for t in tools:
                oa_tools.append({"type": "function", "function": {
                    "name": t.name, "description": t.description, "parameters": t.inputSchema}})
                tool_session[t.name] = session
        print("전체 도구:", list(tool_session))

        for q in ["안녕하세요 Alice!", "15 더하기 25는?", "지금 몇 시?", "부산 날씨는?", "파일 삭제해줘"]:
            print(f"\n질문: {q}")
            r = await gpt.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": q}],
                tools=oa_tools, tool_choice="auto",
            )
            msg = r.choices[0].message
            if not msg.tool_calls:                 # 적합한 도구 없음 → 바로 답
                print(f"답변: {msg.content}")
                continue
            call = msg.tool_calls[0]
            args = json.loads(call.function.arguments)
            print(f"  선택: {call.function.name}({args})  → 해당 서버 세션으로 실행")
            result = await tool_session[call.function.name].call_tool(call.function.name, args)
            print(f"답변: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   전체 도구: ['hello', 'add', 'current_time', 'weather']   ← 두 서버의 도구 합본
#   질문: 15 더하기 25는?
#     선택: add({'a': 15, 'b': 25})  → 해당 서버 세션으로 실행   (add 는 math_server)
#   답변: 15 + 25 = 40
#   질문: 부산 날씨는?
#     선택: weather({'city': '부산'})                          (weather 는 utility_server)
#   → 도구가 어느 서버에 있든 tool_session 매핑으로 올바른 세션에 라우팅된다.
