# client1_pydantic.py
# Pydantic(BaseTool) 기반이지만, 호출할 때마다 MCP에 잠깐 연결하는 초간단 버전

import asyncio

from langchain.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPHelloTool(BaseTool):
    """입력 이름으로 MCP 서버(server.py)의 say_hello 도구를 호출합니다."""
    name: str = "mcp_say_hello"
    description: str = "입력된 이름으로 인사말을 생성합니다"

    # 동기 경로는 사용하지 않도록 차단
    def _run(self, *args, **kwargs):
        raise RuntimeError("동기 실행은 지원하지 않습니다. 비동기(_arun)만 사용하세요.")

    async def _arun(self, name: str) -> str:
        server_params = StdioServerParameters(
            command="python",
            args=["server.py"],  # server.py 안에 say_hello 도구가 있어야 합니다.
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("say_hello", {"name": name})
                    if not result.content:
                        return "빈 응답"
                    item = result.content[0]
                    return getattr(item, "text", str(item))
        except Exception as e:
            return f"MCP 호출 오류: {e}"


async def main():
    tool = MCPHelloTool()
    # 도구를 직접 호출(Agent 없이 간단 테스트)
    print(await tool._arun("John"))
    print(await tool._arun("Alice"))


if __name__ == "__main__":
    asyncio.run(main())
