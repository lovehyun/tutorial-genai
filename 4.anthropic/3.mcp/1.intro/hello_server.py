from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloWorld")

@mcp.tool()
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
