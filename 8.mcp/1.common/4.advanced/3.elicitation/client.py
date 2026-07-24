"""
Elicitation 클라이언트 — 서버가 되묻는 '확인 요청' 을 사용자 대신 응답한다.

ClientSession(..., elicitation_callback=...) 로 콜백을 등록한다.
서버가 ctx.elicit(...) 를 부르면 이 콜백이 실행되고, 여기서 ElicitResult 를 만들어
"승인/거절/취소" 와 폼 데이터를 돌려준다.

실제 앱이라면 이 콜백 안에서 터미널 input() 이나 GUI 다이얼로그로 사용자에게 물어본다.
여기서는 두 시나리오를 순서대로 자동 응답해 흐름을 보여준다.

실행:  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams, ElicitResult

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")


# 데모용: 첫 요청은 승인, 두 번째 요청은 취소하도록 카운터를 둔다
_call_count = {"n": 0}


# ── 서버의 ctx.elicit 요청을 처리하는 콜백 ──────────────────────────
# 시그니처(mcp 1.13): async (context, params) -> ElicitResult | ErrorData
async def elicitation_callback(
    context: RequestContext,
    params: ElicitRequestParams,
) -> ElicitResult:
    print(f"\n[사용자에게 물음] {params.message}")

    _call_count["n"] += 1
    if _call_count["n"] == 1:
        # 실제라면: confirm = input("삭제? (y/n) ") == "y"
        print("   → (자동 응답) 승인 + 사유 입력")
        return ElicitResult(action="accept", content={"confirm": True, "reason": "임시파일 정리"})
    else:
        print("   → (자동 응답) 취소")
        return ElicitResult(action="cancel")


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        # ★ elicitation_callback 등록
        async with ClientSession(read, write, elicitation_callback=elicitation_callback) as session:
            await session.initialize()

            for path in ["/tmp/cache.log", "/tmp/important.db"]:
                result = await session.call_tool("delete_file", {"path": path})
                print("[결과]", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
