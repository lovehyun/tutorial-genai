"""
mcp-math 로컬 서버 — llm-math 와 같은 계산 개념을 MCP 서버로 노출한다.
클라이언트가 stdio 로 이 파일을 자식 프로세스로 띄워 호출한다.

TODO: 아래 add 도구를 완성하세요. hello 는 이미 완성돼 있으니 패턴을 그대로 따라 하면 된다.
"""

import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathServer")


@mcp.tool()
def hello(name: str = "World") -> str:
    """친근한 인사말을 생성합니다."""
    print(f"[MATH_SERVER] hello 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}! 저는 수학 서버입니다."


# TODO: 두 숫자를 더하는 MCP 도구를 완성하세요.
#   힌트 1 — hello 처럼 함수 위에 @mcp.tool() 데코레이터를 붙인다.
#   힌트 2 — 인자 a, b(둘 다 float)를 받아 "a + b = 결과" 형식의 문자열을 반환한다.
#   힌트 3 — hello 처럼 print(..., file=sys.stderr) 로 호출 로그도 남겨보자(선택).
def add(a: float, b: float) -> str:
    pass  # ← 여기를 채우세요 (그리고 함수 위에 @mcp.tool() 도 잊지 말 것)


if __name__ == "__main__":
    print("[MATH_SERVER] 수학 서버 시작됨", file=sys.stderr)
    print("[MATH_SERVER] 제공 기능: hello, add", file=sys.stderr)
    mcp.run()
