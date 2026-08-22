# 2.fs_mcp_client2_config.py — config.json 으로 설정을 분리한 MCP 파일 클라이언트
# 1.fs_mcp_client 와 동일한 '진짜 MCP' 흐름이되, 서버 경로·데모 질문을 config.json 에서 읽는다.
#   (하드코딩 대신 설정 파일로 — 서버를 바꾸려면 config.json 만 수정)

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
CFG = json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8"))
SERVER = os.path.normpath(os.path.join(HERE, CFG["server_path"]))
SERVER_CWD = os.path.normpath(os.path.join(HERE, CFG["server_cwd"]))


def to_openai(tools):
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]


async def main():
    params = StdioServerParameters(command="python", args=[SERVER], cwd=SERVER_CWD)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            oa_tools = to_openai((await session.list_tools()).tools)
            print("설정:", CFG["server_path"], "/ 도구:", [t["function"]["name"] for t in oa_tools])

            for q in CFG["demo_questions"]:
                print(f"\n사용자: {q}")
                r = await gpt.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": q}],
                    tools=oa_tools, tool_choice="auto")
                msg = r.choices[0].message
                if not msg.tool_calls:
                    print(f"AI: {msg.content}")
                    continue
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments)
                print(f"  도구: {call.function.name}({args})")
                result = await session.call_tool(call.function.name, args)
                print(f"  결과: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   설정: ../1.filesystem/server/server.py / 도구: ['list_files', 'read_file', 'rename_file', 'copy_file']
#   사용자: workspace 에 어떤 파일들이 있어?
#     도구: list_files({})
#     결과: {"files": ["hello.txt", "sample.txt", "test.txt"], "count": 3}
#   → 1.fs_mcp_client 와 동작은 같고, 서버 경로·질문을 config.json 에서 읽어온다는 점만 다르다.
