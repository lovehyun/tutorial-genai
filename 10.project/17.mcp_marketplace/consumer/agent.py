"""
consumer/agent.py — 게이트웨이만 보고 동작하는 에이전트.

핵심: 이 에이전트는 '팀 서버 주소'를 전혀 모른다.
      오직 마켓플레이스 게이트웨이의 '내 컨슈머 엔드포인트' 한 곳에만 붙는다.
        URL = {MARKET}/mcp/consumers/<consumer_id>
      그러면 게이트웨이가 내가 '구독한' 서버들의 도구를 'serverid__tool' 로 합쳐서 준다.
      실제 호출도 전부 게이트웨이를 거쳐 각 팀 서버로 중계된다(직접 연결 X).

  구독을 바꾸려면 마켓플레이스 UI(/) 또는 PUT /api/consumers/<id>/subscriptions.
  편의를 위해, 컨슈머가 없거나 구독이 비어 있으면 등록된 서버 전체를 자동 구독한다.

실행:
  pip install requests langchain-openai langchain-mcp-adapters langgraph python-dotenv
  # OPENAI_API_KEY 설정
  python agent.py                       # 기본 컨슈머 travel-agent
  python agent.py shopping-agent
  python agent.py travel-agent "도쿄 여행 예약하고 거기 날씨도 알려줘"   # 단발 질의
"""

import os
import sys
import asyncio

import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

MARKET = os.getenv("MARKET_URL", "http://localhost:8000")   # 마켓플레이스(등록서버+게이트웨이)
TOKEN = os.getenv("MARKET_TOKEN", "").strip()               # 공유 Bearer 토큰(설정 시)
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}   # 쓰기 API + 게이트웨이에 사용

SYSTEM = (
    "너는 사용자를 돕는 에이전트다. 도구 이름은 '서버id__도구명' 형식이며, 여러 외부 팀의 "
    "MCP 서버에서 마켓플레이스를 통해 가져온 것이다. 요청에 맞는 도구를 골라 처리하고, "
    "복합 요청은 여러 도구를 순서대로 사용하라. '예약/주문해줘'면 실제 완료 도구까지 호출하라."
)


def ensure_consumer(consumer_id: str) -> None:
    """컨슈머가 없으면 만들고, 구독이 비었으면 등록된 서버 전체를 구독한다(데모 편의)."""
    subs = requests.get(f"{MARKET}/api/consumers/{consumer_id}/subscriptions", timeout=10)
    if subs.status_code == 404:
        requests.post(f"{MARKET}/api/consumers", timeout=10, headers=HEADERS,
                      json={"id": consumer_id, "name": consumer_id})
        subs = requests.get(f"{MARKET}/api/consumers/{consumer_id}/subscriptions", timeout=10)
    if not subs.json():
        all_ids = [s["id"] for s in requests.get(f"{MARKET}/api/servers", timeout=10).json()]
        requests.put(f"{MARKET}/api/consumers/{consumer_id}/subscriptions", timeout=10, headers=HEADERS,
                     json={"server_ids": all_ids})
        print(f"[setup] '{consumer_id}' 구독 자동 설정: {all_ids}")


async def build_agent(consumer_id: str):
    ensure_consumer(consumer_id)
    url = f"{MARKET}/mcp/consumers/{consumer_id}"
    print(f"게이트웨이 연결: {url}")

    # 게이트웨이(MCP)는 토큰 불필요 — 그냥 붙는다. (토큰은 컨슈머 생성/구독 같은 관리에만)
    client = MultiServerMCPClient({"market": {
        "url": url, "transport": "streamable_http",
    }})
    tools = await client.get_tools()
    if not tools:
        raise SystemExit("도구가 없습니다. 데모 서버가 떠 있고(셀프등록) 구독이 있는지 확인하세요.")
    print("사용 가능한 도구:", [t.name for t in tools])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_agent(llm, tools, system_prompt=SYSTEM)


async def ask(agent, message: str):
    result = await agent.ainvoke({"messages": [("user", message)]})
    used = [c["name"] for m in result["messages"] for c in (getattr(m, "tool_calls", []) or [])]
    print("\n[사용한 도구]", used or "(없음)")
    print("[답변]", result["messages"][-1].content)


async def main():
    consumer_id = sys.argv[1] if len(sys.argv) > 1 else "travel-agent"
    agent = await build_agent(consumer_id)

    if len(sys.argv) > 2:
        await ask(agent, " ".join(sys.argv[2:]))
        return

    print("\n질문을 입력하세요 (종료: exit). 예) 도쿄 여행 예약하고 거기 날씨도 알려줘")
    while True:
        try:
            msg = input("\n나> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if msg.lower() in ("exit", "quit", "종료"):
            break
        if msg:
            await ask(agent, msg)


if __name__ == "__main__":
    asyncio.run(main())
