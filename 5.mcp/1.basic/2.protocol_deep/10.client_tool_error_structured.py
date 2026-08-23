# pip install mcp
#
# isError 와 structuredContent 를 클라이언트 쪽에서 어떻게 구분해서 처리하는지 본다.
# 핵심: call_tool() 은 실패해도 예외를 던지지 않는다(프로토콜 레벨 에러가 아닌 한) —
# 결과 객체의 .isError 를 반드시 직접 확인해야 한다.

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command=sys.executable, args=["9.server_tool_error_structured.py"])


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # [관전 포인트 1] 성공 케이스 — isError=False, content 에 텍스트가 담긴다.
            ok = await session.call_tool("divide", {"a": 10, "b": 2})
            print(f"divide(10,2) → isError={ok.isError}, content={ok.content[0].text}")

            # [관전 포인트 2] 실패 케이스 — 예외가 여기까지 안 올라온다! isError=True 를 직접 확인해야 한다.
            #   (try/except 로 잡으려 하면 아무것도 안 잡힌다 — 이게 흔한 실수 포인트.)
            fail = await session.call_tool("divide", {"a": 10, "b": 0})
            print(f"divide(10,0) → isError={fail.isError}, content={fail.content[0].text}")

            # [관전 포인트 3] structuredContent — Pydantic 모델로 선언한 도구는 파싱 없이 바로 dict 로 온다.
            weather = await session.call_tool("get_weather", {"city": "서울"})
            print(f"get_weather('서울') → structuredContent={weather.structuredContent}")
            print(f"                     content(텍스트 버전)={weather.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
