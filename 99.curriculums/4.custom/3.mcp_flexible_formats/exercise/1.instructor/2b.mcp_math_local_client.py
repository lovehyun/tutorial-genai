"""
mcp-math 로컬 클라이언트 — 2a.mcp_math_local_server.py 를 stdio 로 띄워 도구를 직접 호출한다.
아직 LLM/에이전트는 없다 — 연결과 call_tool 이 되는지 raw 하게 확인만.

원본: 5.mcp/2.openai/2.multi_tools/1.math_client.py
"""

import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "2a.mcp_math_local_server.py"  # 서버 스크립트 파일명


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

            # 1) 도구 목록 확인
            tools_result = await session.list_tools()
            print("사용 가능 도구:")
            for t in tools_result.tools:
                print(f"  - {t.name}: {t.description}")

            # 2) hello 호출
            hello_res = await session.call_tool("hello", {"name": "Alice"})
            print("hello 결과:", _extract_text(hello_res))

            # 3) add 호출
            add_res = await session.call_tool("add", {"a": 5, "b": 7})
            print("add 결과:", _extract_text(add_res))


if __name__ == "__main__":
    asyncio.run(main())


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# 사용 가능 도구:
#   - hello: 친근한 인사말을 생성합니다.
#   - add: 두 숫자를 더합니다.
# hello 결과: Hello, Alice! 저는 수학 서버입니다.
# add 결과: 5.0 + 7.0 = 12.0
#
# (서버가 stderr 로 [MATH_SERVER] 시작됨/호출됨 로그도 함께 찍는다 — 정상)
