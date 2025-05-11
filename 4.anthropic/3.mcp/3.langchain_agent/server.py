from mcp.server.fastmcp import FastMCP

mcp = FastMCP("HelloLangchain")

@mcp.tool()
def say_hello(name: str) -> dict:
    return {"greeting": f"Hello, {name}!"}

if __name__ == "__main__":
    mcp.run()
