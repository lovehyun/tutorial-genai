import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SimpleServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    print(f"[SERVER] hello 함수 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("[SERVER] 서버 시작됨", file=sys.stderr)
    mcp.run()
