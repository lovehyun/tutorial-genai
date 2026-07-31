"""
6.client_interactive.py — 원격 주가 서버에 직접 질문하는 대화형 클라이언트.

2·4·5 는 질문이 코드에 하드코딩돼 있었다(재현 가능한 데모용).
여기서는 터미널에서 직접 물어보며 대화를 이어간다.

새로 등장하는 것:
  - 멀티턴 기억 — checkpointer + 고정 thread_id 로 이전 대화를 기억한다.
      "애플 주가 알려줘" → "그럼 마이크로소프트는?" → "둘 중 뭐가 더 올랐어?"
    처럼 앞 문맥을 이어받는다. (하드코딩 데모에선 매번 새 대화라 이게 안 된다)
  - 도구 호출 실황 표시 — 답이 나오기까지 어떤 원격 도구를 몇 번 불렀는지 보여준다.

준비:
  pip install mcp yfinance langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
  .env 에 OPENAI_API_KEY

실행:
  터미널 1)  python 3.server_stock.py        ← 먼저 서버를 띄워둔다
  터미널 2)  python 6.client_interactive.py
  종료: quit / exit / 종료  또는 Ctrl+C
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

SERVER_URL = "http://127.0.0.1:8001/mcp"
EXIT_WORDS = {"quit", "exit", "종료", "q"}

SYSTEM_PROMPT = """너는 주식 정보 도우미다.

규칙:
- 시세·기업 정보는 반드시 제공된 도구로 조회한다. 기억이나 추측으로 숫자를 말하지 않는다.
- 사용자가 회사 이름으로 물으면 티커로 바꿔 조회한다.
  (애플→AAPL, 마이크로소프트→MSFT, 엔비디아→NVDA, 테슬라→TSLA, 삼성전자→005930.KS, 카카오→035720.KS)
- 도구가 오류 메시지를 돌려주면 티커 형식을 고쳐 한 번 더 시도한다.
- 앞선 대화에서 이미 조회한 종목을 사용자가 '그거', '아까 그 회사' 로 가리키면 그 종목으로 이해한다.
  단, 수치는 다시 조회해서 최신 값을 쓴다.
- 답변은 한국어로, 조회한 수치를 근거로 간결하게 정리한다.
- 투자 판단이나 매매 추천은 하지 않는다. 데이터 요약까지만 한다."""

EXAMPLES = [
    "애플 주가 알려줘",
    "그럼 마이크로소프트는?",
    "둘 중 최근 1개월 더 오른 쪽은?",
    "엔비디아는 어떤 회사야?",
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

    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),      # ← 대화 이력 보관 (멀티턴의 조건)
    )
    # 대화 내내 같은 thread_id → '그럼 ~는?' 같은 이어지는 질문이 통한다
    config = {"configurable": {"thread_id": "stock-chat"}}

    print("=" * 60)
    print(f"주식 정보 도우미 (원격 서버: {SERVER_URL})")
    print(f"  도구: {[t.name for t in tools]}")
    print("  예시:", " / ".join(EXAMPLES[:3]))
    print("  종료: quit / exit / 종료")
    print("=" * 60)

    while True:
        try:
            question = input("\n[나] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not question:
            continue
        if question.lower() in EXIT_WORDS:
            print("종료합니다.")
            break

        try:
            result = await agent.ainvoke({"messages": [("user", question)]}, config=config)
        except Exception as e:
            print(f"\n[오류] {type(e).__name__}: {e}")
            continue

        # 이번 턴에 부른 도구만 보여준다 (이전 턴 메시지는 상태에 계속 쌓이므로 뒤에서부터 훑는다)
        for m in reversed(result["messages"]):
            if m.type == "human":                    # 이번 턴 사용자 메시지에 닿으면 중단
                break
            if getattr(m, "tool_calls", None):
                for c in m.tool_calls:
                    print(f"  → 원격 도구: {c['name']}({c['args']})")

        print(f"\n[도우미] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - 원격 HTTP 서버라도 대화형 앱을 만드는 데 특별한 코드가 필요 없다 — 설정 딕셔너리만 url 이면 된다.
#   - 멀티턴의 조건은 checkpointer + 고정 thread_id 두 개뿐이다.
#   - 여기엔 승인 절차가 없다(조회 전용 서버라 위험한 작업이 없음).
#     삭제·발송처럼 되돌릴 수 없는 도구가 섞이면 승인 게이트를 붙여야 한다 → 6.human_in_loop/
