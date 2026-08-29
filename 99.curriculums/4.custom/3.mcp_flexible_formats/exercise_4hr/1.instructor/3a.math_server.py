"""
5b/5c 라우팅 실습이 쓰는 지원 서버 — 이 파일 자체는 실습 대상이 아니다.

원본: 5.mcp/2.openai/2.multi_tools/math_server.py
"""

import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathServer")


@mcp.tool()
def hello(name: str = "World") -> str:
    """친근한 인사말을 생성합니다."""
    print(f"[MATH_SERVER] hello 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}! 저는 수학 서버입니다."


@mcp.tool()
def add(a: float, b: float) -> str:
    """두 숫자를 더합니다."""
    print(f"[MATH_SERVER] add 호출됨: {a} + {b}", file=sys.stderr)
    result = a + b
    return f"{a} + {b} = {result}"


if __name__ == "__main__":
    mcp.run()


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# 이 서버는 3c/3d 가 stdio 로 자동 실행한다 — 단독 실행 시 대기 상태로 멈춰 있는 게 정상.
# 3c/3d 실행 중 add 가 선택되면 stderr 에 다음이 찍힌다(실제 관측):
#   [MATH_SERVER] add 호출됨: 5.0 + 7.0
