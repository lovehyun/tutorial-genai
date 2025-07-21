from mcp.server.fastmcp import FastMCP
from datetime import datetime
import math

mcp = FastMCP("LangChainMCPServer")

@mcp.tool()
def say_hello(name: str) -> dict:
    """사용자에게 개인화된 인사말을 생성합니다."""
    return {"greeting": f"Hello, {name}!"}

@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수의 덧셈을 계산합니다."""
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """두 수의 곱셈을 계산합니다."""
    return a * b

@mcp.tool()
def now() -> str:
    """현재 시간을 조회합니다."""
    return datetime.now().strftime("현재 시간: %Y-%m-%d %H:%M:%S")

@mcp.tool()
def square_root(number: float) -> float:
    """숫자의 제곱근을 계산합니다."""
    if number < 0:
        raise ValueError("음수의 제곱근은 계산할 수 없습니다.")
    return math.sqrt(number)

@mcp.tool()
def factorial(n: int) -> int:
    """n의 팩토리얼을 계산합니다."""
    if n < 0:
        raise ValueError("음수의 팩토리얼은 정의되지 않습니다.")
    if n == 0 or n == 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    mcp.run()
