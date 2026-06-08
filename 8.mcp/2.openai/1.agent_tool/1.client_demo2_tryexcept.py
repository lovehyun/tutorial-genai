# 1.client_demo2_tryexcept.py — 1.client_demo + 예외 처리
#
# ── 연동 방식 ────────────────────────────────────────────────
#   1.client_demo 와 흐름 동일(initialize → list_tools → call_tool)이되,
#   서버 연결과 각 도구 호출을 try/except 로 감싼다.
#   → 도구가 없거나 인자가 틀려도 raw traceback 대신 "(실패: ...)" 한 줄로 보고.

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def call(session, name, args=None):
    """도구 하나 호출 + 예외를 문자열로"""
    try:
        result = await session.call_tool(name, args or {})
        return result.content[0].text
    except Exception as e:
        return f"(실패: {e})"


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    try:
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                print("도구:", [t.name for t in tools])

                print("hello:", await call(session, "hello", {"name": "John"}))
                print("add  :", await call(session, "add", {"a": 5, "b": 7}))
                print("now  :", await call(session, "now"))
    except Exception as e:
        print(f"서버 연결 실패: {e} — server.py 가 같은 폴더에 있는지 확인")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now']
#   hello: Hello, John!
#   add  : 12
#   now  : 지금 시간은 2026-06-09 ... 입니다.
#   (존재하지 않는 도구를 부르면 → "(실패: Unknown tool ...)" 로 안전하게 보고)
