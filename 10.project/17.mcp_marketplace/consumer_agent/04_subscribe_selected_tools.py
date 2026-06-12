"""
예제 ④ 원하는 서버 '안에서' 원하는 도구만 — 도구 단위 선택.

  마켓플레이스의 구독은 '서버 단위'다(도구 단위 구독은 없다).
  그래서 서버는 구독하되, 게이트웨이가 합쳐 주는 'serverid__tool' 목록을
  '클라이언트에서 걸러' 쓰고 싶은 도구만 남긴다. (LLM 없이 순수 MCP 클라이언트로 확인)

실행:
  pip install mcp requests python-dotenv
  python 04_subscribe_selected_tools.py
  #  → 구독 서버의 전체 도구와, 내가 고른 도구만 출력하고 그중 하나를 실제 호출한다.

  LLM 에이전트에 적용하려면: 아래 filtered(고른 도구)만 create_agent 에 넘기면 된다.
  (전체 에이전트 예시는 agent.py 참고)
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from _market import ensure_consumer, gateway_url, set_subscriptions

CONSUMER = "tool-picky"
SUBSCRIBE_SERVERS = ["weather", "travel"]                 # 서버는 둘 다 구독하지만…
WANT_TOOLS = {"weather__get_weather", "travel__search_trips"}   # …이 도구만 쓴다.


async def main() -> None:
    # 1) 서버 구독은 평소대로(서버 단위)
    ensure_consumer(CONSUMER)
    set_subscriptions(CONSUMER, SUBSCRIBE_SERVERS)

    # 2) 게이트웨이에 붙어 도구 목록을 받고, 클라이언트에서 거른다
    async with streamablehttp_client(gateway_url(CONSUMER)) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            all_names = [t.name for t in (await session.list_tools()).tools]
            filtered = [n for n in all_names if n in WANT_TOOLS]

            print("구독 서버의 모든 도구 :", all_names)
            print("내가 고른 도구만     :", filtered)
            missing = WANT_TOOLS - set(all_names)
            if missing:
                print("⚠ 게이트웨이에 없는 도구(구독/이름 확인):", sorted(missing))

            # 3) 고른 도구 중 하나를 실제 호출(데모)
            if "weather__get_weather" in filtered:
                out = await session.call_tool("weather__get_weather", {"city": "서울"})
                print("\nweather__get_weather('서울') →", out.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
