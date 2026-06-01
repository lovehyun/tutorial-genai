"""
웹 검색 도구 — 실시간 정보가 필요한 에이전트의 필수 도구.
이 예제: Tavily 를 메인으로, Serper / Google CSE 대안을 주석으로 보여줍니다.

LLM 의 지식은 cut-off 가 있어서 "오늘 날씨", "환율", "최근 뉴스" 같은 건 모릅니다.
웹 검색 도구로 보강.

세 가지 옵션 비교:
  1) Tavily  — LLM / RAG 전용 최적화. 결과가 깔끔. 무료 tier 있음. (TAVILY_API_KEY)
                LangChain 공식 권장.
  2) Serper  — Google 검색 결과 그대로. 저렴. (SERPER_API_KEY)
  3) Google CSE — Google Custom Search Engine. (GOOGLE_API_KEY + GOOGLE_CSE_ID)

  ※ pip install langchain-tavily  (또는 langchain-community 안에 Serper / Google)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()


# ─── (1) Tavily — 권장 ─────────────────────────────────────
from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=5,
    topic="general",   # "general" | "news"
)


# ─── (2) Serper — 대안 ─────────────────────────────────────
# from langchain_community.utilities import GoogleSerperAPIWrapper
# from langchain_core.tools import Tool
#
# serper = GoogleSerperAPIWrapper()
# web_search = Tool(
#     name="google_serper",
#     func=serper.run,
#     description="Real-time web search via Google (Serper API).",
# )


# ─── (3) Google CSE — 대안 2 ───────────────────────────────
# from langchain_community.utilities import GoogleSearchAPIWrapper
# from langchain_core.tools import Tool
#
# google = GoogleSearchAPIWrapper(k=5)
# web_search = Tool(
#     name="google_search",
#     func=google.run,
#     description="Real-time web search via Google Custom Search.",
# )


system_prompt = """\
당신은 실시간 정보 검색이 가능한 한국어 어시스턴트입니다.
- 날씨, 뉴스, 환율, 가격, 일정 등 "지금 이 순간" 의 정보는 반드시 web_search 도구로 확인하세요.
- 같은 질문으로 도구를 **2번 이상 부르지 마세요** (검색어 살짝 바꿔서 재시도 금지).
- 검색 결과로 충분히 답할 수 있으면 즉시 종료. 결과가 빈약해도 그 안에서 답하세요.
- LLM 자체 지식은 cut-off date 이후 정보를 모릅니다.
- 검색 결과를 출처(URL) 와 함께 한국어로 요약해주세요.
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [web_search], system_prompt=system_prompt)


for q in ["오늘 서울 날씨 어때?", "LangChain 의 최신 버전이 뭐야?"]:
    print("\n" + "=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke(
        {"messages": [("user", q)]},
        config={"recursion_limit": 15},
    )

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 검색: {c['name']}({c['args']})")
        if m.type == "tool":
            preview = m.content[:150] if isinstance(m.content, str) else str(m.content)[:150]
            print(f"  ← 결과: {preview}...")

    print(f"\n[답변] {result['messages'][-1].content}")
