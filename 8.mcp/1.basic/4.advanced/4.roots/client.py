"""
Roots 클라이언트 — 서버에게 '작업 허용 경로' 목록을 제공한다.

ClientSession(..., list_roots_callback=...) 로 콜백을 등록한다.
서버가 ctx.session.list_roots() 를 부르면 이 콜백이 실행되어 Root 목록을 돌려준다.

실제 IDE 라면 '현재 열린 워크스페이스 폴더들' 을 여기서 반환한다.

실행:  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from mcp.types import ListRootsResult, Root

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")


# ── 서버의 roots/list 요청에 응답하는 콜백 ──────────────────────────
# 시그니처(mcp 1.13): async (context) -> ListRootsResult | ErrorData
async def list_roots_callback(context: RequestContext) -> ListRootsResult:
    return ListRootsResult(
        roots=[
            # uri 는 file:// 필수. FileUrl 로 검증된다.
            Root(uri="file:///workspace", name="내 워크스페이스"),
            Root(uri="file:///tmp/shared", name="공유 폴더"),
        ]
    )


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        # ★ list_roots_callback 등록
        async with ClientSession(read, write, list_roots_callback=list_roots_callback) as session:
            await session.initialize()

            r1 = await session.call_tool("show_roots", {})
            print("[show_roots]\n" + r1.content[0].text)

            print("\n[is_allowed]")
            for p in ["/workspace/main.py", "/etc/passwd", "/tmp/shared/a.txt"]:
                r = await session.call_tool("is_allowed", {"path": p})
                print("  " + r.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
