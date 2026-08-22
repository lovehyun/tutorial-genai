# 3.fs_mcp_client3_gpt.py — 자연어 파일 관리 '대화형' 챗봇 (진짜 MCP)
# 1/2 는 정해진 질문을 한 번에 처리, 여기는 멀티턴 — 사용자가 직접 명령을 입력한다.
#   예: "파일 목록 보여줘" / "test.txt 읽어줘" / "a.txt 를 b.txt 로 복사" / quit

import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
gpt = AsyncOpenAI()

HERE = os.path.dirname(os.path.abspath(__file__))
FS_DIR = os.path.normpath(os.path.join(HERE, "..", "1.filesystem"))
SERVER = os.path.join(FS_DIR, "server", "server.py")


def to_openai(tools):
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]


async def handle(session, oa_tools, text):
    r = await gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}],
        tools=oa_tools, tool_choice="auto")
    msg = r.choices[0].message
    if not msg.tool_calls:
        print(f"  AI: {msg.content}")
        return
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    print(f"  도구: {call.function.name}({args})")
    result = await session.call_tool(call.function.name, args)
    print(f"  결과: {result.content[0].text}")


async def main():
    params = StdioServerParameters(command="python", args=[SERVER], cwd=FS_DIR)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            oa_tools = to_openai((await session.list_tools()).tools)
            print("파일 챗봇 (quit 으로 종료). 예: '파일 목록', 'test.txt 읽어줘'")
            loop = asyncio.get_event_loop()
            while True:
                text = (await loop.run_in_executor(None, input, "\n명령> ")).strip()
                if text.lower() in ("quit", "exit", "종료"):
                    break
                if text:
                    await handle(session, oa_tools, text)


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   파일 챗봇 (quit 으로 종료). 예: '파일 목록', 'test.txt 읽어줘'
#   명령> 파일 목록 보여줘
#     도구: list_files({})
#     결과: {"files": ["hello.txt", "sample.txt", "test.txt"], "count": 3}
#   명령> test.txt 읽어줘
#     도구: read_file({'filename': 'test.txt'})
#     결과: {"content": "test\ntest1234\n"}
#   명령> quit
#   → 1/2 는 정해진 질문 배치, 여기는 멀티턴 — 같은 세션을 유지하며 계속 명령을 받는다.
