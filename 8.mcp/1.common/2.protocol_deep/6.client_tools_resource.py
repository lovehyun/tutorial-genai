# 6.client_tools_resource.py — tool(실행) vs resource(읽기) 를 직접 비교하는 클라이언트
# 5.server_tools_resource.py 와 짝. call_tool(도구 실행) ↔ read_resource(데이터 읽기) 차이를 본다.

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    params = StdioServerParameters(command="python", args=["5.server_tools_resource.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # ── 도구(tool): 목록 + '실행'(call_tool) ──
            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])
            print("  add(3, 5)              →", (await session.call_tool("add", {"a": 3, "b": 5})).content[0].text)
            print("  word_count('MCP 정말 쉽다') →", (await session.call_tool("word_count", {"text": "MCP 정말 쉽다"})).content[0].text)

            # ── 리소스(resource): 목록 + '읽기'(read_resource) ──
            # 실행이 아니라 URI 로 식별되는 읽기 전용 데이터를 가져온다.
            resources = (await session.list_resources()).resources
            print("\n리소스:", [str(r.uri) for r in resources])
            info = await session.read_resource("info://server")
            print("  read_resource('info://server') →", info.contents[0].text)


if __name__ == "__main__":
    asyncio.run(main())
