import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(command="python", args=["hello_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("hello", {"name": "John"})
            print(result.content[0].text)  # → 'Hello, John!'

if __name__ == "__main__":
    asyncio.run(main())
