# pip install mcp
#
# 취소(Cancellation) — 오래 걸리는 도구를 클라이언트가 도중에 그만두게 할 수 있다.
# progress_logging(2번)이 "진행 상황을 보여주는" 채널이었다면, 이건 "그만 시켜"를 보내는 채널이다.
# 이 서버는 진행률을 흘리면서 도는 slow_task 하나뿐 — client.py 가 이걸 중간에 취소한다.

import asyncio
import sys
from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("cancellation-demo")


@mcp.tool()
async def slow_task(ctx: Context, seconds: int = 10) -> str:
    """seconds초 동안 1초 간격으로 진행률을 흘리며 도는 느린 작업."""
    try:
        for i in range(seconds):
            await asyncio.sleep(1)
            await ctx.report_progress(i + 1, seconds, f"{i + 1}/{seconds}초 진행")
        return "완료"
    except asyncio.CancelledError:
        # [관전 포인트] 클라이언트가 취소 알림을 보내면 SDK가 이 태스크를 asyncio 레벨에서
        #   취소한다 — 여기서 asyncio.CancelledError로 잡힌다. 정리 작업(임시파일 삭제 등)이
        #   필요하면 여기서 하고 반드시 다시 raise 해서 취소를 완성시켜야 한다.
        print(f"[server] slow_task 취소됨 (진행 중이던 시점에서 중단)", file=sys.stderr)
        raise


if __name__ == "__main__":
    mcp.run(transport="stdio")
