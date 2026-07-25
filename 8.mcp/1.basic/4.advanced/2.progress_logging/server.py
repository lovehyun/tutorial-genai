"""
MCP 심화 (2) Progress + Logging — 오래 걸리는 도구의 '중간 상황' 을 흘려보낸다.

도구가 5초, 50초 걸리는 작업이라면 클라이언트는 그동안 깜깜하다.
MCP 는 도구 실행 도중 서버가 클라이언트에게 두 가지를 보낼 수 있게 한다:
  - 진행률(progress)  : ctx.report_progress(progress, total, message)
  - 로그(log)         : ctx.info("...") / ctx.debug/warning/error(...)

이 둘은 모두 Context 객체(ctx)로 접근한다. 도구 함수의 인자에 ctx: Context 를
추가하면 FastMCP 가 자동으로 주입한다(클라이언트 인자로는 보이지 않음).

준비:  pip install mcp
실행:  python client.py
"""

import asyncio

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("progress-demo")


@mcp.tool()
async def batch_job(items: int, ctx: Context) -> str:
    """items 개의 작업을 순차 처리하면서 진행률과 로그를 실시간으로 보낸다."""
    await ctx.info(f"작업 시작 — 총 {items}개")   # 클라이언트 logging_callback 으로 전달

    done = 0
    for i in range(items):
        await asyncio.sleep(0.3)                  # 실제 처리를 흉내
        done += 1
        # progress/total 로 몇 % 인지, message 로 사람이 읽을 설명을 함께 보낸다
        await ctx.report_progress(progress=done, total=items, message=f"{done}/{items} 처리")
        if done == items // 2:
            await ctx.warning("절반 지점 통과 — 잠깐 느려질 수 있음")  # 경고 로그 예시

    await ctx.info("작업 완료")
    return f"{items}개 처리 완료"


if __name__ == "__main__":
    mcp.run()

# 정리:
#   - report_progress 는 '진행 막대' 용, info/warning/error 는 '로그 스트림' 용.
#   - 클라이언트가 받으려면: call_tool(..., progress_callback=...) + ClientSession(logging_callback=...).
#   - stdout 오염 금지 규칙은 그대로 — 로그는 print() 가 아니라 ctx.info() 로 보낸다.
