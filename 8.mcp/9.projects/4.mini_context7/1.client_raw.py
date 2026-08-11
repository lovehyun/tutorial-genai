"""
mini-context7 클라이언트 #1 — 순수 MCP 클라이언트 (LangChain 없음).
resolve_library_id → get_library_docs 2단계 흐름을 손으로 호출해 보고,
등록 안 된 ID로 바로 요청했을 때 서버가 거부하는 것(가드레일)도 확인한다.

API 키 불필요 — 이 서버는 LLM/임베딩을 쓰지 않는다.
"""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")


async def main():
    params = StdioServerParameters(command="python", args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("도구:", [t.name for t in tools.tools], "\n")

            # 1) 이름만 알고 정확한 ID는 모른다 → resolve 먼저
            print("=== resolve_library_id('fastapi') ===")
            resolved = await session.call_tool("resolve_library_id", {"libraryName": "fastapi"})
            print(resolved.content[0].text, "\n")

            # 2) resolve 가 알려준 ID로, topic 을 좁혀서 문서 조회
            print("=== get_library_docs('/tiangolo/fastapi', topic='쿼리') ===")
            docs = await session.call_tool(
                "get_library_docs",
                {"context7_compatible_library_id": "/tiangolo/fastapi", "topic": "쿼리"},
            )
            print(docs.content[0].text, "\n")

            # 3) 가드레일 확인 — resolve 없이 등록 안 된 ID로 바로 요청하면?
            print("=== get_library_docs('/facebook/react') — 등록 안 된 ID ===")
            bad = await session.call_tool(
                "get_library_docs",
                {"context7_compatible_library_id": "/facebook/react"},
            )
            print(bad.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
