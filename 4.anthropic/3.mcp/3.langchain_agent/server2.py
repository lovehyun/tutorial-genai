from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloLangchain")

@mcp.tool()
def say_hello(name: str) -> dict:
    return {"greeting": f"Hello, {name}!"}

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool()
def now() -> str:
    from datetime import datetime
    return datetime.now().strftime("현재 시간: %Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    mcp.run()
