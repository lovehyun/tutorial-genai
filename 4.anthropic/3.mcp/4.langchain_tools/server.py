from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("MultiToolServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def now() -> str:
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")

if __name__ == "__main__":
    mcp.run()
