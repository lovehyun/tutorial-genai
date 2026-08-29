"""
mcp-math 로컬 클라이언트 — 2a.mcp_math_local_server.py 를 stdio 로 띄워 도구를 직접 호출한다.
아직 LLM/에이전트는 없다 — 연결과 call_tool 이 되는지 raw 하게 확인만.

DONE — 2.student(todo) 의 add 호출 TODO 를 채운 정답.
"""

import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "2a.mcp_math_local_server.py"


def _extract_text(result) -> str:
    """MCP call_tool 응답에서 텍스트를 안전하게 추출"""
    if hasattr(result, "content") and result.content:
        item = result.content[0]
        return getattr(item, "text", None) or str(item)
    return ""


async def main():
    params = StdioServerParameters(command=sys.executable, args=[SERVER_FILE])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("사용 가능 도구:")
            for t in tools_result.tools:
                print(f"  - {t.name}: {t.description}")

            # 완성된 예시 — hello 호출
            hello_res = await session.call_tool("hello", {"name": "Alice"})
            print("hello 결과:", _extract_text(hello_res))

            # DONE: hello 호출과 같은 패턴으로 완성
            #   힌트 — session.call_tool("add", {"a": 5, "b": 7}) ← 채움
            add_res = await session.call_tool("add", {"a": 5, "b": 7})  # ← 채움
            print("add 결과:", _extract_text(add_res))


if __name__ == "__main__":
    asyncio.run(main())
