import sys
from mcp.server.fastmcp import FastMCP

# 수학 관련 기능을 제공하는 서버
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
