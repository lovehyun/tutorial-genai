# server.py - MCP 서버
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("MultiToolServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    """사용자에게 인사하는 함수"""
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수를 더하는 함수"""
    return a + b

@mcp.tool()
def now() -> str:
    """현재 시간을 반환하는 함수"""
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")

if __name__ == "__main__":
    mcp.run()
