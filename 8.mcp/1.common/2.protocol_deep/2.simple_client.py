# 2.simple_client.py — 도구를 호출하면서 '오가는 JSON-RPC'를 눈으로 본다 (debug_proxy 경유)
#
# ── 연동 방식 ────────────────────────────────────────────────
#   클라이언트 → [debug_proxy.py] → 1.simple_server.py
#   debug_proxy 가 클라↔서버 사이에 끼어 모든 메시지를 debug_proxy.log 에 기록한다.
#   흐름 자체는 평범하다: initialize → list_tools → call_tool. 다른 점은 '중간에서 엿본다'는 것.
#   (프록시 없이 서버에 바로 붙으려면 args=["1.simple_server.py"] 로만 바꾸면 됨)

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # 이전 로그 삭제 후, 프록시를 통해 서버에 연결
    if os.path.exists("debug_proxy.log"):
        os.remove("debug_proxy.log")
    server_params = StdioServerParameters(
        command="python", args=["debug_proxy.py", "1.simple_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # 핸드셰이크
            
            tools = (await session.list_tools()).tools
            print("[CLIENT] 도구:", [t.name for t in tools])

            print("[CLIENT] hello(John)  →", (await session.call_tool("hello", {"name": "John"})).content[0].text)
            print("[CLIENT] hello(Alice) →", (await session.call_tool("hello", {"name": "Alice"})).content[0].text)

    # 프록시가 기록한 JSON-RPC 원문 보기 (이 파일의 핵심)
    await asyncio.sleep(0.3)
    print("\n===== 프록시가 본 JSON-RPC (debug_proxy.log) =====")
    if os.path.exists("debug_proxy.log"):
        print(open("debug_proxy.log", encoding="utf-8").read())


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   [CLIENT] 도구: ['hello']
#   [CLIENT] hello(John)  → Hello, John!
#   [CLIENT] hello(Alice) → Hello, Alice!
#   ===== 프록시가 본 JSON-RPC =====
#   [C->S] {"method":"initialize", ...}
#   [S->C] {"result":{"protocolVersion": ...}}
#   [C->S] {"method":"tools/call","params":{"name":"hello","arguments":{"name":"John"}}}  ← 도구 호출
#   [S->C] {"result":{"content":[{"type":"text","text":"Hello, John!"}]}}
