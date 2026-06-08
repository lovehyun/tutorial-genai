# 1.client_demo.py — 가장 단순한 MCP 클라이언트: 도구를 '수동으로' 직접 호출 (LLM 없음)
#
# ── 연동 방식 (MCP 핵심 3동작) ───────────────────────────────
#   1) stdio_client 가 server.py 를 '자식 프로세스'로 실행하고 stdin/stdout 파이프로 연결
#   2) session.initialize() — 핸드셰이크(프로토콜 버전·기능 협상)
#   3) session.list_tools() 로 도구 발견 → session.call_tool(이름, 인자) 로 실행
#   ※ 여기선 '어떤 도구를 어떤 인자로' 부를지 내가 손으로 정한다(수동 하드코딩).
#     다음 단계: 2.client_simple_nlp(키워드 자동) → 3.client_gpt(LLM 자동)

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # 1) 서버를 자식 프로세스(stdio)로 띄운다
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 2) 핸드셰이크 — 이후부터 list_tools / call_tool 가능
            await session.initialize()

            # 3) 도구 발견: 서버가 어떤 도구를 제공하는지 조회
            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])

            # 4) 도구 호출 — 어떤 도구·인자를 쓸지 '내가 직접' 결정 (수동)
            #    call_tool 결과는 content 블록 리스트 → [0].text 로 텍스트를 꺼낸다
            print("hello:", (await session.call_tool("hello", {"name": "John"})).content[0].text)
            print("add  :", (await session.call_tool("add", {"a": 5, "b": 7})).content[0].text)
            print("now  :", (await session.call_tool("now")).content[0].text)
    # async with 블록을 벗어나면 서버 프로세스·파이프가 자동 정리된다


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now']
#   hello: Hello, John!
#   add  : 12
#   now  : 지금 시간은 2026-06-09 04:04:03 입니다.
