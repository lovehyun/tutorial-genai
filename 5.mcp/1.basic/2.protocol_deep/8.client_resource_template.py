# pip install mcp
#
# 리소스 템플릿을 실제로 호출해본다 — 서버가 정의한 {변수}에 값을 채워 URI를 완성해서 read_resource
# 하면 된다. 클라이언트 입장에선 정적 리소스와 호출 방식이 완전히 같다(read_resource(uri)) —
# "템플릿이었는지"는 서버 쪽 구현 디테일이고 클라이언트는 신경 쓸 필요 없다.
#
# 덤: initialize() 가 돌려주는 InitializeResult 에 서버와 협상된 capabilities 가 담겨 있다 —
# 지금까지는 텍스트로만 설명했던 "capability negotiation"을 여기서 직접 눈으로 확인한다.

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(command=sys.executable, args=["7.server_resource_template.py"])


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            init_result = await session.initialize()

            # [관전 포인트 1] capability negotiation을 직접 확인 — 서버가 tools/resources/prompts
            #   중 무엇을 지원한다고 선언했는지가 여기 담겨 있다. 1.basic/4.advanced의 sampling·
            #   elicitation·roots도 이 협상(클라이언트 쪽 capability)이 먼저 있어야 동작한다.
            print("협상된 capabilities:", init_result.capabilities)
            print("서버 정보:", init_result.serverInfo)

            # [관전 포인트 2] URI에 값을 직접 채워서 read_resource — 템플릿이든 아니든 호출법은 동일.
            r1 = await session.read_resource("greeting://Alice")
            print("\ngreeting://Alice →", r1.contents[0].text)

            r2 = await session.read_resource("user://1/profile/role")
            print("user://1/profile/role →", r2.contents[0].text)

            r3 = await session.read_resource("user://999/profile/name")
            print("user://999/profile/name →", r3.contents[0].text)  # 없는 id → 서버가 처리한 메시지


if __name__ == "__main__":
    asyncio.run(main())
