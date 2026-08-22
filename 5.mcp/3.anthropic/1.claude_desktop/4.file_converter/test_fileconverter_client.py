import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path

async def main():
    server = StdioServerParameters(command=sys.executable, args=["file_converter_server.py"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Downloads 폴더에서 "인공지능" 검색
            res = await session.call_tool("find", {"query": "인공지능"})
            print(res)

if __name__ == "__main__":
    asyncio.run(main())
