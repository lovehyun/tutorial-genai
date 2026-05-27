"""
복합 에이전트 — 여러 도구 + 메모리 + HITL 종합 응용

이 파일은 앞 모든 예제의 종합:
  - bind_tools / @tool (1.basics, 3.custom_tools)
  - 빌트인 도구 (2.builtin_tools)
  - create_react_agent (4.langgraph_react/4.1)
  - MemorySaver (4.langgraph_react/4.2)
  - 멀티 도구 라우팅 (5.1_routing)

시나리오: "여행 계획 어시스턴트"
  - 날씨 조회 (web search)
  - 일정 계산 (math)
  - 명소 정보 (wikipedia)
  - 대화 메모리 유지 (thread_id 기준)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


# ─── 도구 1: 가짜 날씨 조회 (실전엔 4.3 web_search 의 Tavily 사용) ─────
@tool
def get_weather_forecast(city: str, days_ahead: int = 0) -> str:
    """도시의 날씨 예보를 가져온다.
    Args:
        city: 도시 이름 (예: '서울')
        days_ahead: 며칠 후 (0=오늘, 1=내일, ...)
    """
    # 데모용 가짜 데이터
    forecast = {
        ("서울", 0): "맑음, 22도",
        ("서울", 1): "구름 많음, 20도",
        ("부산", 0): "흐림, 25도",
        ("부산", 1): "비, 23도",
        ("제주", 0): "맑음, 24도",
        ("제주", 1): "맑음, 25도",
    }
    return forecast.get((city, days_ahead), f"{city} 의 {days_ahead}일 후 예보 정보 없음")


# ─── 도구 2: 계산기 ─────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 계산. 입력 예: '50000 * 3 + 20000'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"


# ─── 도구 3: 위키피디아 ─────────────────────────────────────
wiki_ko = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="ko", top_k_results=2, doc_content_chars_max=1500),
    name="wikipedia_ko",
    description="한국어 위키피디아 검색. 관광지/도시/인물 정보.",
)


# ─── 시스템 프롬프트 — 페르소나 + 도구 가이드 ──────────────
system_prompt = """\
당신은 한국어로 여행을 계획해주는 친절한 어시스턴트입니다.

가능한 도구:
- get_weather_forecast: 도시의 날씨 예보 (며칠 후까지)
- calculator: 비용 계산, 거리/시간 계산 등 수학
- wikipedia_ko: 관광지/도시/명소 등 사실 정보

원칙:
1) 사용자 요구를 단계별로 분해해서 필요한 도구를 차례로 호출
2) 추측 금지 — 정보 부족하면 도구로 확인하거나 사용자에게 추가 질문
3) 최종 답변은 한국어로, 구조화된 형식 (목록/표 등) 으로

이전 대화 내용을 기억하고 연결해서 답하세요.
"""


# ─── 에이전트 + 메모리 ─────────────────────────────────────
checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

agent = create_react_agent(
    llm,
    [get_weather_forecast, calculator, wiki_ko],
    prompt=system_prompt,
    checkpointer=checkpointer,
)


# ─── 멀티턴 대화 시나리오 ───────────────────────────────────
config = {"configurable": {"thread_id": "trip-planning-001"}}


def chat(user_input: str):
    print("\n" + "=" * 60)
    print(f"[user] {user_input}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", user_input)]}, config=config)

    # 도구 호출 추적
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → {c['name']}({c['args']})")

    print(f"\n[ai] {result['messages'][-1].content}")


# 4 turns — 메모리로 컨텍스트 연결
chat("제주도로 1박2일 여행 가려고 해. 오늘이랑 내일 날씨 어때?")
chat("제주도에서 꼭 가봐야 할 관광지 추천해줘.")
chat("렌터카 1일 50000원, 숙박 1박 120000원, 식비 1일 30000원이면 총 비용 얼마야?")
chat("아까 내가 어디 여행 간다고 했지?")     # ← 메모리 확인


# ─────────────────────────────────────────────────────────
# 이 에이전트가 보여주는 것:
#   1. 여러 도구를 자유롭게 라우팅
#   2. 도구 결과를 자연스럽게 종합
#   3. 멀티턴 대화 컨텍스트 유지 (thread_id)
#   4. 추측 없이 도구로 사실 확인
#
# 다음 단계 (이 디렉토리에는 없음):
#   - interrupt 로 사용자 승인 받기 (4.langgraph_react/4.3_interrupt.py)
#   - 도구 결과를 RAG 와 결합 (../7.RAG/5.agentic/)
#   - LangGraph 로 명시적 워크플로우 (../9.langgraph/)
# ─────────────────────────────────────────────────────────
