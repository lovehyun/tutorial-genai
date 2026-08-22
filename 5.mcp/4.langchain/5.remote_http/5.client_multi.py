"""
5.client_multi.py — 두 '원격' MCP 서버를 한 에이전트에 동시에 붙인다.

1.quickstart/4.multi_server.py 와 같은 그림이지만, 거기선 서버를 전부 stdio 로 직접 띄웠다.
여기선 둘 다 이미 떠 있는 HTTP 서버다 — 실무에서 흔한 형태:
  "사내 공용 MCP 서버 여러 대 + 각자 노트북의 에이전트"

핵심:
  - MultiServerMCPClient 는 {이름: 설정} 딕셔너리다. 서버를 늘리려면 항목만 추가하면 된다.
  - get_tools() 는 모든 서버의 도구를 하나의 리스트로 합쳐준다 (에이전트는 출처를 신경 쓰지 않는다).
  - stdio 서버와 http 서버를 한 딕셔너리에 섞어도 된다 (아래 주석 참고).

실행:
  터미널 1)  python 1.server_simple.py     (8000)
  터미널 2)  python 3.server_stock.py      (8001)
  터미널 3)  python 5.client_multi.py
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

SYSTEM_PROMPT = """너는 여러 도구를 조합해 답하는 도우미다.
시세·기업 정보는 반드시 도구로 조회하고, 추측으로 숫자를 말하지 않는다.
회사 이름은 티커로 바꿔 조회한다 (애플→AAPL, 엔비디아→NVDA, 삼성전자→005930.KS).
답변은 한국어로 간결하게 정리하고, 투자 추천은 하지 않는다."""


async def main():
    # ─── 서버를 늘리고 싶으면 항목만 추가 — 코드 구조는 그대로 ──
    client = MultiServerMCPClient({
        "toolbox": {                                   # 1.server_simple.py
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable_http",
        },
        "stock": {                                     # 3.server_stock.py
            "url": "http://127.0.0.1:8001/mcp",
            "transport": "streamable_http",
        },
        # stdio 서버를 섞어 쓰고 싶다면 이런 항목을 그냥 추가하면 된다:
        # "local": {"command": "python", "args": ["../4.tools_safety/server.py"], "transport": "stdio"},
    })

    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"[연결 실패] {type(e).__name__}: {e}")
        print("→ 1.server_simple.py(8000) 와 3.server_stock.py(8001) 가 모두 떠 있는지 확인하세요.")
        return

    print(f"두 서버의 도구가 하나로 합쳐짐 — 총 {len(tools)}개:")
    for t in tools:
        print(f"  - {t.name}")
    print()

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

    # 두 서버의 도구가 한 흐름에서 협력하도록 유도한 질문
    #   now(8000 서버) + get_stock_price/get_company_info(8001 서버)
    question = "지금 서버 시각을 알려주고, 엔비디아가 어떤 회사인지와 현재 주가도 함께 정리해줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구: {c['name']}({c['args']})")

    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - 에이전트 입장에서 도구가 어느 서버(어느 전송 방식) 에서 왔는지는 전혀 중요하지 않다.
#     그래서 '도구를 만드는 쪽' 과 '도구를 쓰는 쪽' 을 완전히 분리할 수 있다 — 이게 MCP 의 값어치.
#   - 서버 이름("toolbox"/"stock") 은 설정 식별용이며, 도구 이름은 원래 이름 그대로 노출된다.
#     → 서버 간에 도구 이름이 겹치지 않도록 설계하는 게 좋다.
