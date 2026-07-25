"""
Progress + Logging 클라이언트 — 도구 실행 도중 오는 진행률/로그를 실시간으로 받는다.

두 채널을 각각 다른 곳에 등록한다:
  - 진행률 → session.call_tool(..., progress_callback=...)
  - 로그   → ClientSession(..., logging_callback=...)

실행:  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")


# ── 로그 콜백: 서버의 ctx.info/warning/error 가 여기로 온다 ──────────
# 시그니처(mcp 1.13): async (params) -> None
async def logging_callback(params: LoggingMessageNotificationParams) -> None:
    print(f"   [LOG:{params.level}] {params.data}")


# ── 진행률 콜백: 서버의 ctx.report_progress 가 여기로 온다 ──────────
# 시그니처: async (progress, total, message) -> None
async def progress_callback(progress: float, total: float | None, message: str | None) -> None:
    pct = f"{progress/total*100:5.1f}%" if total else f"{progress}"
    print(f"   [진행률 {pct}] {message or ''}")


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        # ★ 로그는 세션 단위로 등록
        async with ClientSession(read, write, logging_callback=logging_callback) as session:
            await session.initialize()

            print("[클라이언트] batch_job(items=6) 호출 — 진행 상황이 실시간으로 흐른다:")
            # ★ 진행률은 이 호출에만 붙이는 콜백
            result = await session.call_tool(
                "batch_job",
                {"items": 6},
                progress_callback=progress_callback,
            )
            print("[클라이언트] 최종 결과:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
