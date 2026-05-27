"""
웹 검색 도구 — Tavily / Serper / Google Search 비교

실시간 정보가 필요한 에이전트의 필수 도구. 세 가지 옵션:

1) **Tavily**  — LLM/RAG 전용으로 최적화. 결과가 깔끔. (TAVILY_API_KEY)
2) **Serper**  — Google 검색 결과 그대로. 저렴. (SERPER_API_KEY)
3) **GoogleSearchAPIWrapper** — Google Custom Search Engine. (GOOGLE_API_KEY + GOOGLE_CSE_ID)

이 파일은 **Tavily** 를 메인으로, Serper 와 Google 은 주석 처리로 보여줌.
LangChain 2026 기준 신규 프로젝트는 Tavily 추천 (LangChain 공식 권장).
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# pip install langchain-tavily   (or)   pip install google-search-results
# .env 에 TAVILY_API_KEY=... 필요

load_dotenv()


# ─── (1) Tavily — 권장 ─────────────────────────────────────
from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=5,
    topic="general",   # "general" | "news"
)
# name 은 자동으로 "tavily_search" 같은 게 들어감


# ─── (2) Serper — 대안 ─────────────────────────────────────
# from langchain_community.utilities import GoogleSerperAPIWrapper
# from langchain_core.tools import Tool
#
# serper = GoogleSerperAPIWrapper()
# web_search = Tool(
#     name="google_serper",
#     func=serper.run,
#     description="Real-time web search via Google (Serper API). 최신 뉴스/실시간 정보.",
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


# ─── 시스템 프롬프트 ──────────────────────────────────────
system_prompt = """\
당신은 실시간 정보 검색이 가능한 한국어 어시스턴트입니다.
- 날씨, 뉴스, 환율, 가격, 일정 등 "지금 이 순간" 의 정보는 반드시 web_search 도구로 확인하세요.
- LLM 자체 지식은 cut-off date 이후 정보를 모릅니다.
- 검색 결과를 출처(URL)와 함께 한국어로 요약해주세요.
"""


# ─── 에이전트 ─────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [web_search], prompt=system_prompt)


# ─── 실행 ─────────────────────────────────────────────────
questions = [
    "오늘 서울 날씨 어때?",
    "LangChain 의 최신 버전이 뭐야?",
]

for q in questions:
    print("=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", q)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 검색 호출: {c['name']}({c['args']})")
        if m.type == "tool":
            content_preview = m.content[:150] if isinstance(m.content, str) else str(m.content)[:150]
            print(f"  ← 검색 결과: {content_preview}...")

    print(f"\n[최종 답변]\n{result['messages'][-1].content}\n")
