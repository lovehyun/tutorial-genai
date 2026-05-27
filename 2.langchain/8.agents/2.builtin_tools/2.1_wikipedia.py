"""
Wikipedia 빌트인 도구 — create_react_agent 와 결합

LangChain Community 의 `WikipediaQueryRun` 을 도구로 사용한다.
한국어 (`lang="ko"`) / 영어 (`lang="en"`) 등 언어 옵션, 결과 개수 제한 가능.

legacy 의 0.legacy/1.wikipedia/2.1~2.5 를 현행 LangGraph API 로 통합·간소화한 버전.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langgraph.prebuilt import create_react_agent

# pip install wikipedia

load_dotenv()


# ─── 한국어 Wikipedia 도구 ─────────────────────────────────
wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        lang="ko",
        top_k_results=3,
        doc_content_chars_max=2000,
    ),
    name="wikipedia_ko",
    description="한국어 위키피디아에서 사실/배경 정보를 검색한다. 인물, 사건, 개념 등.",
)


# ─── (옵션) 영어 Wikipedia 도구도 같이 ─────────────────────
wiki_en = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        lang="en",
        top_k_results=3,
        doc_content_chars_max=2000,
    ),
    name="wikipedia_en",
    description="English Wikipedia. Use for global topics or when Korean info is insufficient.",
)


# ─── 시스템 프롬프트 (한국어로 답변 강제) ───────────────────
system_prompt = """\
당신은 위키피디아를 활용해 사실 기반의 답변을 제공하는 한국어 비서입니다.
- 사실/날짜/인물 정보는 반드시 위키피디아 도구로 확인한 후 답하세요.
- 한국 관련 주제는 wikipedia_ko 를, 글로벌/영어권 주제는 wikipedia_en 을 사용하세요.
- 추측하지 말고, 도구 결과에 없는 정보는 "모른다" 고 답하세요.
- 출력은 한국어, 간결하게 (5문장 이내).
"""


# ─── LangGraph 에이전트 ────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [wiki_ko, wiki_en], prompt=system_prompt)


# ─── 실행 ─────────────────────────────────────────────────
questions = [
    "세종대왕은 누구이고 어떤 업적을 남겼어?",
    "Python 프로그래밍 언어는 누가 만들었어?",
]

for q in questions:
    print("=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", q)]})

    # 도구 호출 흐름 출력
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 도구 결과: {m.content[:100]}...")

    print(f"\n[최종 답변]\n{result['messages'][-1].content}\n")


# ─────────────────────────────────────────────────────────
# Legacy 대비:
#   ❌ initialize_agent(tools, llm, AgentType.ZERO_SHOT_REACT_DESCRIPTION, ...)
#   ✅ create_react_agent(llm, tools, prompt=system_prompt)
#
# - system prompt 가 더 깔끔하게 전달됨
# - 결과가 messages 리스트로 와서 도구 호출 흐름 추적 쉬움
# - max_iterations 등은 RunnableConfig 로 제어
# ─────────────────────────────────────────────────────────
