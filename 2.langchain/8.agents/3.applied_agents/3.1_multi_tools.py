"""
다중 도구 + 자동 라우팅 — LLM 이 알아서 어떤 도구를 부를지 결정.
이 예제: 계산기 + 날씨 + 시간 3가지 도구를 등록하고, 질문에 따라 다른 도구가 호출되는 걸 관찰.

핵심:
  - 도구 여러 개를 그냥 리스트로 넘기면 됨
  - LLM (특히 gpt-4o 계열) 은 tool calling 정확도가 높아 명시적 라우터 불필요
  - 도구가 필요 없는 질문은 도구를 안 부르고 직접 답함
  - 한 질문에 여러 도구가 연쇄로 호출되기도 함 (자동 ReAct 루프)
"""

from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent   # (구) langgraph.prebuilt.create_react_agent

load_dotenv()


# ─── 도구 3종 ──────────────────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 조회한다 (데모 데이터)."""
    return {"서울": "맑음, 22도", "부산": "흐림, 25도", "제주": "맑음, 24도"}.get(
        city, f"{city} 날씨 정보 없음"
    )


@tool
def get_current_time() -> str:
    """현재 시각을 반환한다."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ─── 에이전트 — 도구 리스트만 넘기면 끝 ─────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator, get_weather, get_current_time])


# ─── 다양한 질문으로 라우팅 관찰 ───────────────────────
questions = [
    "153 * 7 은?",                              # → calculator
    "서울 날씨 어때?",                          # → get_weather
    "지금 몇 시야?",                             # → get_current_time
    "서울이랑 부산 날씨 둘 다 알려주고, 22 * 7 도 계산해줘.",  # → 여러 도구 연쇄
    "오늘 기분이 좀 그래.",                       # → 도구 없이 직접 답
]


for q in questions:
    print("\n" + "=" * 60)
    print(f"[질문] {q}")
    print("=" * 60)
    result = agent.invoke({"messages": [("user", q)]})

    tools_used = [
        c["name"]
        for m in result["messages"]
        if hasattr(m, "tool_calls") and m.tool_calls
        for c in m.tool_calls
    ]
    print(f"[사용 도구] {tools_used or '(없음 — 직접 답변)'}")
    print(f"[답변] {result['messages'][-1].content}")
