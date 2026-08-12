"""
mcp-math 로컬 서버 — llm-math 와 같은 계산 개념을 MCP 서버로 노출한다.
클라이언트가 stdio 로 이 파일을 자식 프로세스로 띄워 호출한다.

DONE — 2.student(todo) 의 add 도구 TODO 를 채운 정답.
"""

import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathServer")


@mcp.tool()
def hello(name: str = "World") -> str:
    """친근한 인사말을 생성합니다."""
    print(f"[MATH_SERVER] hello 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}! 저는 수학 서버입니다."


# DONE: hello 와 같은 패턴으로 완성
#   힌트 1 — hello 처럼 함수 위에 @mcp.tool() 데코레이터를 붙인다. ← 채움
#   힌트 2 — 인자 a, b(둘 다 float)를 받아 "a + b = 결과" 형식의 문자열을 반환한다. ← 채움
#   힌트 3 — hello 처럼 print(..., file=sys.stderr) 로 호출 로그도 남긴다. ← 채움
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
