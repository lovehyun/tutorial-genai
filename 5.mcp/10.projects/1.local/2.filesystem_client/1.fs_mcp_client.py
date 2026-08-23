# 1.fs_mcp_client.py — 자연어 파일 작업을 '진짜 MCP' 로 처리하는 클라이언트
# 우리 파일시스템 MCP 서버(../1.filesystem/server/server.py)를 띄우고,
# GPT function calling 으로 list_files / read_file / rename_file / copy_file 을 자동 호출한다.
#   ※ 서버의 작업 폴더(WORK_DIR="./workspace")가 항상 같은 곳을 가리키도록 cwd 로 서버 디렉터리를 지정.

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
FS_DIR = os.path.normpath(os.path.join(HERE, "..", "1.filesystem"))   # 여기 아래에 workspace/ 가 있음
SERVER = os.path.join(FS_DIR, "server", "server.py")


def to_openai(tools):
    """MCP 도구 스키마 → OpenAI function calling 형식"""
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]


async def main():
    params = StdioServerParameters(command="python", args=[SERVER], cwd=FS_DIR)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            oa_tools = to_openai(tools)
            print("도구:", [t.name for t in tools])

            for q in ["workspace 에 어떤 파일들이 있어?",
                      "test.txt 내용을 읽어줘",
                      "hello.txt 를 backup.txt 로 복사해줘"]:
                print(f"\n사용자: {q}")
                r = await gpt.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": q}],
                    tools=oa_tools, tool_choice="auto",
                )
                msg = r.choices[0].message
                if not msg.tool_calls:
                    print(f"AI: {msg.content}")
                    continue
                call = msg.tool_calls[0]
                args = json.loads(call.function.arguments)
                print(f"  선택된 도구: {call.function.name}({args})")
                result = await session.call_tool(call.function.name, args)
                print(f"  결과: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['list_files', 'read_file', 'rename_file', 'copy_file']
#   사용자: workspace 에 어떤 파일들이 있어?
#     선택된 도구: list_files({})
#     결과: {"files": ["hello.txt", "sample.txt", "test.txt"], "count": 3}
#   사용자: test.txt 내용을 읽어줘
#     선택된 도구: read_file({'filename': 'test.txt'})
#     결과: {"content": "test\ntest1234\n"}
#   → GPT 가 자연어를 보고 list_files/read_file/copy_file 중 알맞은 MCP 도구를 자동 선택.
