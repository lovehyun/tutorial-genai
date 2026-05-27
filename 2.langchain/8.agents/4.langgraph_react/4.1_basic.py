"""
LangGraph create_react_agent — 현행 권장 에이전트

bind_tools (1.2) 는 도구 호출 1회만 처리하지만,
create_react_agent 는 **자동으로 ReAct 루프** (Thought → Action → Observation → ...) 를 돌린다.
도구 호출이 끝날 때까지 (또는 max iteration 까지) 알아서 반복.

→ legacy `initialize_agent(... AgentType.ZERO_SHOT_REACT_DESCRIPTION)` 의 현행 대체품.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()


# ─── 1. 도구 정의 (앞 예제와 동일) ──────────────────────────
@tool
def add(a: int, b: int) -> int:
    """두 정수를 더한다."""
    return a + b

@tool
def multiply(a: int, b: int) -> int:
    """두 정수를 곱한다."""
    return a * b

@tool
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 조회한다."""
    return {"서울": "맑음, 22도", "부산": "흐림, 25도"}.get(city, "정보 없음")


# ─── 2. LangGraph 에이전트 생성 ─────────────────────────────
# 한 줄로 ReAct 루프 자동화 (도구 호출 → 결과 → 다음 결정 ... 반복)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_react_agent(llm, [add, multiply, get_weather])


# ─── 3. 실행 — 메시지 리스트 형태로 입력 ────────────────────
print("=" * 60)
print("(1) 단일 도구 호출")
print("=" * 60)
result = agent.invoke({"messages": [("user", "3 더하기 5 는?")]})

# 결과에는 전체 대화 흐름이 messages 로 들어 있음
for m in result["messages"]:
    print(f"\n[{m.type}]")
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  tool_call: {c['name']}({c['args']})")
    if m.content:
        print(f"  content: {m.content}")


print("\n" + "=" * 60)
print("(2) 다단계 — 자동 루프")
print("=" * 60)
result = agent.invoke({
    "messages": [("user", "3 + 5 의 결과에 7 을 곱한 값과, 서울 날씨를 알려줘.")]
})

for m in result["messages"]:
    print(f"\n[{m.type}]")
    if hasattr(m, "tool_calls") and m.tool_calls:
        for c in m.tool_calls:
            print(f"  tool_call: {c['name']}({c['args']})")
    if m.content:
        print(f"  content: {m.content[:200]}")


# ─────────────────────────────────────────────────────────
# 차이점 (legacy vs 현행):
#
#   ❌ Legacy (0.legacy(initialize_agent)/ 의 예제들):
#       from langchain.agents import initialize_agent, AgentType
#       agent = initialize_agent(tools, llm, AgentType.ZERO_SHOT_REACT_DESCRIPTION)
#       → LangChain v0.2+ deprecated
#
#   ✅ 현행 (이 파일):
#       from langgraph.prebuilt import create_react_agent
#       agent = create_react_agent(llm, tools)
#       → 표준 형식 (messages 기반), 메모리/interrupt 등과 자연스럽게 결합
#
# 다음: 3.2_with_memory.py — 메모리 추가, 3.3_interrupt.py — human-in-the-loop
# ─────────────────────────────────────────────────────────
