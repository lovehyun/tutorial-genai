"""
금융 조회 봇 (CLI) — 뉴스/기업정보/환율/주가 도구를 가진 create_agent.
이 앱: 자연어로 물으면 LLM 이 알맞은 도구를 골라 답한다 (멀티툴 라우팅의 실전 응용).

실행:  python app.py
       → 데모 질문 3개 자동 실행 후, 대화형 입력 (빈 줄 / quit 로 종료)

  ※ pip install langchain langchain-openai requests yfinance python-dotenv
  ※ .env (상위 2.langchain/.env 또는 이 폴더 .env):
       OPENAI_API_KEY (필수)
       NAVER_CLIENT_ID / NAVER_CLIENT_SECRET (뉴스, 선택)
       SERPER_API_KEY (기업정보, 선택)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from finance_tools import TOOLS

load_dotenv()

SYSTEM = """당신은 금융 정보 비서입니다. 뉴스·기업정보·환율·주가 도구를 활용해 한국어로 간결히 답하세요.
- 환율/주가 같은 숫자는 반드시 도구로 확인 (추측 금지)
- 한국 주식 티커는 '005930.KS'(삼성전자) 형식
- 출처 링크가 있으면 함께 제시"""

agent = create_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), TOOLS, system_prompt=SYSTEM)


def ask(q: str):
    result = agent.invoke({"messages": [("user", q)]})
    used = [c["name"] for m in result["messages"]
            if getattr(m, "tool_calls", None) for c in m.tool_calls]

    print(f"[사용 도구] {used or '(없음 — 직접 답변)'}")
    print(f"[답변] {result['messages'][-1].content}\n")


if __name__ == "__main__":
    print("=== 금융 조회 봇 (데모 질문 먼저) ===\n")
    for q in ["삼성전자 주가 알려줘", "달러 환율 얼마야?", "엔비디아 관련 최근 뉴스 있어?"]:
        print(f"[질문] {q}")
        ask(q)

    print("--- 대화형 (빈 줄/quit 로 종료) ---")
    while True:
        try:
            q = input("질문> ").strip()
        except EOFError:
            break
        
        if not q or q.lower() in ("quit", "exit"):
            break
        
        ask(q)
