# pip install mcp
#
# slow_task 를 시작해놓고 2초 뒤에 취소한다. 서버가 진행률을 흘리다가 중간에 멈추는 걸 확인한다.
#
# ⚠️ 이 SDK 버전은 취소를 위한 공개 헬퍼(예: session.cancel(request_id))를 아직 제공하지 않는다.
#   그래서 이 예제는 session._request_id(다음에 발급될 요청 ID)를 직접 읽어서 취소 알림에 쓴다 —
#   private 속성이라 원래는 지양할 방식이지만, 지금 SDK에서 "취소가 실제로 어떻게 동작하는지"를
#   보여줄 수 있는 유일한 방법이라 여기서는 예외적으로 쓴다. 실전 코드에서는 SDK가 공개 API를
#   제공할 때까지 이 패턴에 의존하지 말 것.

import asyncio
import os
import sys
import mcp.types as types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# env를 명시적으로 넘긴다 — 안 넘기면 서버 프로세스가 부모 셸의 PYTHONIOENCODING 등을
# 못 물려받아 Windows에서 한글 stderr 로그가 깨질 수 있다.
server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
    env={**os.environ, "PYTHONIOENCODING": "utf-8"},
)


# progress_callback은 반드시 async 함수여야 한다(SDK가 await로 호출한다) — sync 함수를 넘기면
# "NoneType can't be used in 'await' expression" 같은 조용한 오류가 난다.
async def on_progress(progress: float, total: float | None, message: str | None) -> None:
    print(f"[진행률] {message}")


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # [관전 포인트 1] call_tool 을 백그라운드 태스크로 띄운다 — await 로 바로 기다리면
            #   완료될 때까지 아무것도 못 하니, 취소를 보낼 시점을 벌어야 한다.
            next_request_id = session._request_id
            task = asyncio.create_task(
                session.call_tool("slow_task", {"seconds": 10}, progress_callback=on_progress)
            )

            await asyncio.sleep(2.5)  # 몇 초 진행되게 기다린 뒤

            # [관전 포인트 2] CancelledNotification 을 직접 만들어 보낸다 — 취소하려는 요청의
            #   requestId 를 지정해야 서버가 "어떤 작업"을 멈출지 안다.
            print("[client] 취소 알림 전송")
            await session.send_notification(
                types.ClientNotification(
                    types.CancelledNotification(
                        params=types.CancelledNotificationParams(
                            requestId=next_request_id, reason="사용자가 취소함"
                        )
                    )
                )
            )

            # [관전 포인트 3] 취소된 요청을 기다리면 결과 대신 McpError("Request cancelled")가 온다.
            try:
                result = await task
                print("[client] 결과:", result)
            except Exception as e:
                print(f"[client] 취소로 인한 예외: {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
