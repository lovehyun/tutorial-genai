# 1.client_http.py — HTTP(streamable-http) 전송으로 MCP 서버에 붙는 클라이언트
#
# ── 연동 방식 ────────────────────────────────────────────────
#   stdio 와 딱 한 줄만 다르다:
#     stdio : stdio_client(StdioServerParameters(...))  → 서버를 '자식 프로세스'로 실행
#     http  : streamablehttp_client(url)                → 이미 떠 있는 '원격 서버'에 접속
#   세션을 연 뒤 흐름(initialize → list_tools → call_tool)은 stdio 와 완전히 동일하다.
#   ※ 먼저 다른 터미널에서 서버 실행:  python server_http.py  (http://localhost:8000/mcp)

import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://localhost:8000/mcp"


async def main():
    # streamablehttp_client 는 (read, write, _) 세 값을 준다 (stdio 는 두 값)
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 도구 목록 = 이 한 줄. (각 도구의 inputSchema 로 매개변수 상세도 볼 수 있음)
            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])

            # 도구 호출 — 전송이 HTTP 라는 점만 다르고 사용법은 stdio 와 같다
            print("hello:", (await session.call_tool("hello", {"name": "Alice"})).content[0].text)
            print("add  :", (await session.call_tool("add", {"a": 15, "b": 25})).content[0].text)
            print("now  :", (await session.call_tool("now")).content[0].text)


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now']
#   hello: Hello, Alice!
#   add  : 40
#   now  : 지금 시간은 2026-06-09 ... 입니다.
