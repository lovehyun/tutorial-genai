import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            res1 = await session.call_tool("hello", {"name": "John"})
            print("hello tool: ", res1.content[0].text)

            res2 = await session.call_tool("add", {"a": 5, "b": 7})
            print("add tool: ", res2.content[0].text)

            res3 = await session.call_tool("now")
            print("now tool: ", res3.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
