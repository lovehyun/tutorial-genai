"""
mcp-math 로컬 서버 — llm-math 와 같은 계산 개념을 MCP 서버로 노출한다.
클라이언트가 stdio 로 이 파일을 자식 프로세스로 띄워 호출한다.

원본: 8.mcp/2.openai/2.multi_tools/math_server.py
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
    print("[MATH_SERVER] 수학 서버 시작됨", file=sys.stderr)
    print("[MATH_SERVER] 제공 기능: hello, add", file=sys.stderr)
    mcp.run()


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# 이 서버는 2b.mcp_math_local_client.py 가 stdio 로 자동 실행한다 — 단독 실행 시 대기 상태로 멈춰 있는 게 정상.
# 클라이언트가 붙으면 stderr 에 다음이 찍힌다:
#   [MATH_SERVER] 수학 서버 시작됨
#   [MATH_SERVER] 제공 기능: hello, add
#   [MATH_SERVER] hello 호출됨: name=Alice
#   [MATH_SERVER] add 호출됨: 5.0 + 7.0
# 클라이언트 쪽 결과는 2b.mcp_math_local_client.py 하단 참고.
