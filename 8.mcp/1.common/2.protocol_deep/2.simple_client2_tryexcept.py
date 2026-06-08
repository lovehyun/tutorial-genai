# 2.simple_client2_tryexcept.py — 2.simple_client + 예외 처리
#
# ── 연동 방식 ────────────────────────────────────────────────
#   2.simple_client 와 동일(debug_proxy 경유 → 1.simple_server, JSON-RPC 로그 확인)이되,
#   연결과 도구 호출을 try/except 로 감싸 실패해도 깔끔하게 보고하고 로그는 끝까지 출력한다.

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    if os.path.exists("debug_proxy.log"):
        os.remove("debug_proxy.log")
    server_params = StdioServerParameters(
        command="python", args=["debug_proxy.py", "1.simple_server.py"]
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = (await session.list_tools()).tools
                print("[CLIENT] 도구:", [t.name for t in tools])

                for who in ["John", "Alice"]:
                    try:
                        res = await session.call_tool("hello", {"name": who})
                        print(f"[CLIENT] hello({who}) →", res.content[0].text)
                    except Exception as e:
                        print(f"[CLIENT] hello({who}) 실패: {e}")

    except Exception as e:
        print(f"[CLIENT] 연결 실패: {e}")

    # 프록시 로그는 성공/실패와 무관하게 출력
    await asyncio.sleep(0.3)
    
    print("\n===== 프록시가 본 JSON-RPC (debug_proxy.log) =====")
    if os.path.exists("debug_proxy.log"):
        print(open("debug_proxy.log", encoding="utf-8").read())


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   [CLIENT] 도구: ['hello']
#   [CLIENT] hello(John) → Hello, John!
#   [CLIENT] hello(Alice) → Hello, Alice!
#   ===== 프록시가 본 JSON-RPC =====  (initialize / tools/list / tools/call 메시지들)
