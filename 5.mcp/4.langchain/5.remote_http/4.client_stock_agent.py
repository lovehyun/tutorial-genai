"""
4.client_stock_agent.py — 실제 API 서버(3.server_stock.py) 를 쓰는 투자 정보 에이전트.

2.client_agent.py 와 코드 구조는 똑같다(URL 만 8001 로 바뀜).
대신 여기선 '도구가 실제 데이터를 가져올 때 에이전트가 어떻게 달라지는지' 를 본다:

  - LLM 은 오늘 주가를 모른다 → 반드시 도구를 불러야만 답할 수 있다.
    (1.server_simple 의 add 는 LLM 혼자서도 풀 수 있어서 이 점이 잘 안 드러난다)
  - 질문 하나에 도구를 여러 번 부른다. "애플과 마이크로소프트 비교" →
    get_stock_price(AAPL), get_stock_price(MSFT), get_stock_history(...) …
    어떤 순서로 몇 번 부를지는 LLM 이 스스로 계획한다.
  - 티커를 모르면? 사람 말('애플') → 티커('AAPL') 변환은 LLM 의 상식이 담당하고,
    시세 조회는 도구가 담당한다. 이 역할 분담이 에이전트 + MCP 조합의 핵심이다.

준비:
  pip install mcp yfinance langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
  .env 에 OPENAI_API_KEY

실행:
  터미널 1)  python 3.server_stock.py     ← 먼저 서버를 띄워둔다
  터미널 2)  python 4.client_stock_agent.py
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

SERVER_URL = "http://127.0.0.1:8001/mcp"

SYSTEM_PROMPT = """너는 주식 정보 도우미다.

규칙:
- 시세·기업 정보는 반드시 제공된 도구로 조회한다. 절대 기억이나 추측으로 숫자를 말하지 않는다.
- 사용자가 회사 이름으로 물으면 티커로 바꿔서 조회한다.
  (예: 애플→AAPL, 마이크로소프트→MSFT, 엔비디아→NVDA, 삼성전자→005930.KS, 카카오→035720.KS)
- 도구가 오류 메시지를 돌려주면 티커 형식을 고쳐 한 번 더 시도한다.
- 답변은 한국어로, 조회한 수치를 근거로 간결하게 정리한다.
- 투자 판단이나 매매 추천은 하지 않는다. 데이터 요약까지만 한다."""

QUESTIONS = [
    "애플 현재 주가 알려줘.",
    "애플과 마이크로소프트 중 최근 1개월 동안 더 많이 오른 쪽은 어디야?",
    "삼성전자는 어떤 회사이고 지금 주가는 얼마야?",
]


async def main():
    client = MultiServerMCPClient({
        "stock": {
            "url": SERVER_URL,
            "transport": "streamable_http",
        },
    })

    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"[연결 실패] {SERVER_URL} 에 붙지 못했습니다: {type(e).__name__}: {e}")
        print("→ 다른 터미널에서 'python 3.server_stock.py' 를 먼저 실행했는지 확인하세요.")
        return

    print(f"가져온 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)

    for question in QUESTIONS:
        print("=" * 60)
        print(f"[질문] {question}\n")

        result = await agent.ainvoke({"messages": [("user", question)]})

        # 도구 호출과 그 결과를 함께 찍어, LLM 의 '계획' 을 눈으로 확인한다
        for m in result["messages"]:
            if hasattr(m, "tool_calls") and m.tool_calls:
                for c in m.tool_calls:
                    print(f"  → 도구: {c['name']}({c['args']})")
            if getattr(m, "type", None) == "tool":
                head = str(m.content).replace("\n", " / ")[:160]
                print(f"  ← 결과: {head}")

        print(f"\n[답변] {result['messages'][-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - 도구가 '진짜 데이터' 를 물어다 주면 에이전트는 비로소 쓸모가 생긴다.
#   - 시스템 프롬프트로 "숫자는 반드시 도구로" 를 못 박는 게 환각 방지의 핵심
#     (4.tools_safety 에서 배운 가드레일을 실전 서버에 적용한 형태).
#   - 다음: 5.client_multi.py — 두 원격 서버를 한 에이전트에 동시에 붙이기.
