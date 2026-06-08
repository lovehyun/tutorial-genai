"""
멀티 에이전트 (3) — 금융 분석가: 주가(yfinance) worker + 뉴스 worker 를 '병렬' 로 돌려 종합.
이 예제: LangGraph StateGraph 의 fan-out / fan-in — START 에서 두 worker 로 갈라져(병렬) 실행되고,
         둘 다 끝나면 synthesize 노드가 결과를 합쳐 최종 브리핑을 만든다.

왜 create_agent 하나로 안 되나?
  - create_agent 는 'model ↔ tools' ReAct 루프 한 가지 모양만 만든다 (순차).
  - 여기서 필요한 건 "두 작업을 동시에 → 둘 다 끝나면 합치기" 라는 다른 토폴로지.
    이 병렬+합류(barrier)는 StateGraph 로 직접 그려야 한다.

흐름:
               ┌───────────────────┐
   START ─┬──▶│ market (yfinance) │────┐
          │    └───────────────────┘    ▼
          │    ┌───────────────────┐  synthesize ────▶ END
          └──▶│ news (구글 뉴스)   │───┘  (둘 다 끝나야 실행 = 자동 barrier)
               └───────────────────┘
"""

from dotenv import load_dotenv
from typing import TypedDict

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 도구: 주가 (yfinance, 키 불필요) ───────────────────────
@tool
def get_stock_data(ticker: str) -> str:
    """티커 심볼로 최근 5거래일 종가와 등락률을 조회한다. 예: 'AAPL'"""
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="5d")
        if hist.empty:
            return f"{ticker}: 데이터 없음"

        last, first = hist["Close"].iloc[-1], hist["Close"].iloc[0]
        chg = (last - first) / first * 100
        return f"{ticker} 최근 종가 {last:.2f} (5일 {chg:+.1f}%)"
    except Exception as e:
        return f"주가 조회 실패: {e}"


# ─── 도구: 기업 뉴스 (구글 뉴스 RSS, 키 불필요) ─────────────
@tool
def get_company_news(company: str) -> str:
    """회사명으로 최신 뉴스 헤드라인 5개를 가져온다."""
    try:
        import re, requests
        params = {"q": company, "hl": "ko", "gl": "KR", "ceid": "KR:ko"}
        xml = requests.get("https://news.google.com/rss/search",
                           params=params, timeout=10).text
        
        titles = re.findall(r"<title>(.*?)</title>", xml)[1:6]   # [0] 은 피드 제목
        titles = [re.sub(r"<!\[CDATA\[|\]\]>", "", t) for t in titles]
        return "\n".join(f"- {t}" for t in titles) or "뉴스 없음"
    except Exception as e:
        return f"뉴스 조회 실패: {e}"


# ─── worker 에이전트 2명 (각자 도구 보유, 노드가 위임) ──────
market_agent = create_agent(
    llm, [get_stock_data],
    system_prompt="회사명을 받으면 적절한 미국 티커를 추론해 get_stock_data 로 조회하고 핵심만 보고하라.")

news_agent = create_agent(
    llm, [get_company_news],
    system_prompt="회사명을 받아 get_company_news 로 최신 뉴스를 모아 핵심만 요약하라.")


# ─── 그래프 공유 상태 ───────────────────────────────────────
# market / news 는 서로 다른 키에 쓰므로 병렬 실행해도 충돌 없음.
class State(TypedDict):
    company: str
    market: str
    news: str
    answer: str


# ─── 노드들 ─────────────────────────────────────────────────
def market_node(state: State) -> dict:
    print("  [market] yfinance worker 실행")
    r = market_agent.invoke({"messages": [("user", f"{state['company']} 주가 알려줘")]})
    return {"market": r["messages"][-1].content}


def news_node(state: State) -> dict:
    print("  [news] 뉴스 worker 실행")
    r = news_agent.invoke({"messages": [("user", f"{state['company']} 최신 뉴스")]})
    return {"news": r["messages"][-1].content}


def synthesize_node(state: State) -> dict:
    print("  [synthesize] 주가 + 뉴스 종합")
    prompt = (f"다음 자료로 '{state['company']}' 투자 참고용 브리핑을 한국어로 작성하라.\n\n"
              f"[주가]\n{state['market']}\n\n[뉴스]\n{state['news']}\n\n"
              "주가 흐름과 뉴스 분위기를 엮어 2~3문장으로. (투자 권유 아님)")
    return {"answer": llm.invoke(prompt).content}


# ─── 그래프 조립: START 에서 fan-out → synthesize 에서 fan-in ─
g = StateGraph(State)
g.add_node("market", market_node)
g.add_node("news", news_node)
g.add_node("synthesize", synthesize_node)

g.add_edge(START, "market")          # ┐ START 에서 두 엣지가 나가면
g.add_edge(START, "news")            # ┘ market·news 가 '병렬' 실행됨
g.add_edge("market", "synthesize")   # ┐ 둘 다 synthesize 로 모이면
g.add_edge("news", "synthesize")     # ┘ synthesize 는 '둘 다 끝나야' 실행 (자동 barrier)
g.add_edge("synthesize", END)

app = g.compile()


# ─── 실행 ───────────────────────────────────────────────────
company = "Apple"
print(f"분석 대상: {company}\n")
result = app.invoke({"company": company})

print("\n=== 주가 (market worker) ===")
print(result["market"])
print("\n=== 뉴스 (news worker) ===")
print(result["news"])
print("\n=== 종합 브리핑 (synthesize) ===")
print(result["answer"])


# 정리:
#   - START→market, START→news 두 엣지 = 병렬 fan-out (동시 실행)
#   - market→synthesize, news→synthesize = fan-in (synthesize 는 둘 다 끝나야 실행)
#   - 각 worker 는 create_agent 에게 위임, 그래프는 '병렬 + 합류'를 책임 (함수 호출론 직접 못 함)
#   - 같은 StateGraph 계열: 9.agentic_patterns/9.4(오케스트레이터)·9.5(평가-개선 루프)
