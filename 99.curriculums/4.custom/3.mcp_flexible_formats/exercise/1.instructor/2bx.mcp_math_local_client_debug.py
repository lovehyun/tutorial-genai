"""
2b 확장 — 2a.mcp_math_local_server.py 는 그대로 두고, 클라이언트만 debug_proxy.py 를 경유하도록
바꿔서 "call_tool 한 줄"이 실제로는 어떤 JSON-RPC 왕복인지 직접 눈으로 본다.
2b 와 다른 건 딱 하나 — StdioServerParameters 의 args 에 debug_proxy.py 를 한 겹 끼운 것뿐이다.

── 연동 방식 ────────────────────────────────────────────────
  클라이언트 → [debug_proxy.py] → 2a.mcp_math_local_server.py
  debug_proxy 가 클라↔서버 사이에 끼어 모든 메시지를 debug_proxy.log 에 기록한다.
  (프록시 없이 서버에 바로 붙는 원래 방식이 2b — args=[SERVER_FILE] 로만 바뀐 거였다)

원본: 8.mcp/1.basic/2.protocol_deep/2.simple_client.py(프록시 경유 방식) + 이 폴더의 2b
"""

import os
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "2a.mcp_math_local_server.py"  # 2b 와 동일 — 서버는 안 바꾼다


def _extract_text(result) -> str:
    """MCP call_tool 응답에서 텍스트를 안전하게 추출"""
    if hasattr(result, "content") and result.content:
        item = result.content[0]
        return getattr(item, "text", None) or str(item)
    return ""


async def main():
    if os.path.exists("debug_proxy.log"):
        os.remove("debug_proxy.log")

    # 2b 는 args=[SERVER_FILE] 로 서버에 바로 붙었다. 여기선 debug_proxy.py 를 한 겹 끼운다.
    params = StdioServerParameters(command=sys.executable, args=["debug_proxy.py", SERVER_FILE])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("사용 가능 도구:")
            for t in tools_result.tools:
                print(f"  - {t.name}: {t.description}")

            hello_res = await session.call_tool("hello", {"name": "Alice"})
            print("hello 결과:", _extract_text(hello_res))

            add_res = await session.call_tool("add", {"a": 5, "b": 7})
            print("add 결과:", _extract_text(add_res))

    # 프록시가 기록한 JSON-RPC 원문 보기 (2b 에는 없던, 이 파일의 핵심)
    await asyncio.sleep(0.3)
    print("\n===== 프록시가 본 JSON-RPC (debug_proxy.log) =====")
    if os.path.exists("debug_proxy.log"):
        print(open("debug_proxy.log", encoding="utf-8").read())


if __name__ == "__main__":
    asyncio.run(main())


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# 사용 가능 도구:
#   - hello: 친근한 인사말을 생성합니다.
#   - add: 두 숫자를 더합니다.
# hello 결과: Hello, Alice! 저는 수학 서버입니다.
# add 결과: 5.0 + 7.0 = 12.0
#
# ===== 프록시가 본 JSON-RPC (debug_proxy.log) =====
# [PROXY] 서버 시작: 2a.mcp_math_local_server.py
# [PROXY] 메시지 중계 시작
# [C->S] {"method": "initialize", "params": {...}, "jsonrpc": "2.0", "id": 0}
# [S->C] {"jsonrpc": "2.0", "id": 0, "result": {"protocolVersion": "...", "serverInfo": {"name": "MathServer", ...}}}
# [C->S] {"method": "tools/list", "params": {}, "jsonrpc": "2.0", "id": 1}
# [S->C] {"jsonrpc": "2.0", "id": 1, "result": {"tools": [{"name": "hello", ...}, {"name": "add", ...}]}}
# [C->S] {"method": "tools/call", "params": {"name": "hello", "arguments": {"name": "Alice"}}, "jsonrpc": "2.0", "id": 2}
# [S->C] {"jsonrpc": "2.0", "id": 2, "result": {"content": [{"type": "text", "text": "Hello, Alice! 저는 수학 서버입니다."}]}}
# [C->S] {"method": "tools/call", "params": {"name": "add", "arguments": {"a": 5, "b": 7}}, "jsonrpc": "2.0", "id": 3}
# [S->C] {"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": "5.0 + 7.0 = 12.0"}]}}
#
# → 2b 에서 session.call_tool() 두 번으로 감춰져 있던 왕복이, initialize/list_tools/call_tool 을
#   포함해 총 5번의 JSON-RPC 메시지 교환이었다는 게 로그로 드러난다.
