# 1.client_demo.py — 가장 단순한 MCP 클라이언트: 도구를 '수동으로' 직접 호출 (LLM 없음)
#
# 2.openai/1.agent_tool/1.client_demo.py, 3.anthropic/2.anthropic_api/1.client_demo.py 와
# 코드가 100% 동일하다 — LLM이 등장하기 전까진 벤더가 다를 이유가 없다.
#
# ── 연동 방식 (MCP 핵심 3동작) ───────────────────────────────
#   1) stdio_client 가 server.py 를 '자식 프로세스'로 실행하고 stdin/stdout 파이프로 연결
#   2) session.initialize() — 핸드셰이크(프로토콜 버전·기능 협상)
#   3) session.list_tools() 로 도구 발견 → session.call_tool(이름, 인자) 로 실행
#   ※ 여기선 '어떤 도구를 어떤 인자로' 부를지 내가 손으로 정한다(수동 하드코딩).
#     다음 단계: 2.client_manual_nlp(키워드 자동) → 3.client_ollama(로컬 LLM 자동)

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])

            print("hello:", (await session.call_tool("hello", {"name": "John"})).content[0].text)
            print("add  :", (await session.call_tool("add", {"a": 5, "b": 7})).content[0].text)
            print("now  :", (await session.call_tool("now")).content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
