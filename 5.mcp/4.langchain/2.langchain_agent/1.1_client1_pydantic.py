# 1.1_client1_pydantic.py
# Pydantic(BaseTool) 기반으로 MCP 도구를 감싸, 호출할 때마다 MCP 에 잠깐 연결하는 초간단 버전.
# (에이전트 없이 도구만 직접 호출 — 가장 단순한 첫 단계)

import asyncio

from langchain_core.tools import BaseTool          # (구) langchain.tools → 현행 langchain_core.tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPHelloTool(BaseTool):
    """입력 이름으로 MCP 서버(server.py)의 say_hello 도구를 호출합니다."""
    name: str = "mcp_say_hello"
    description: str = "입력된 이름으로 인사말을 생성합니다"

    # 동기 경로는 사용하지 않도록 차단 (MCP 는 본질적으로 async)
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
    # 도구를 직접 호출(Agent 없이 간단 테스트) — 현행 권장 진입점은 .ainvoke()
    print(await tool.ainvoke({"name": "John"}))
    print(await tool.ainvoke({"name": "Alice"}))


if __name__ == "__main__":
    asyncio.run(main())
