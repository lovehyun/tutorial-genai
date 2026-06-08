"""
멀티 에이전트 (2) — 슈퍼바이저 패턴을 LangGraph StateGraph 로 '직접' 구성.
이 예제: START / END + 노드 + 조건부 엣지로 '관리자 → worker → 관리자' 루프를 손으로 짠다.

10.1 과의 차이 — 왜 굳이 그래프를?
  - 10.1 은 create_agent(=이미 컴파일된 LangGraph 그래프)를 '도구처럼' 중첩 호출했다.
    동작은 하지만 그래프 구조(노드/엣지/분기)가 코드에 드러나지 않는다.
  - 여기서는 StateGraph 로 노드·엣지를 직접 그린다 → 흐름 제어가 눈에 보이고,
    조건부 라우팅·반복·상태 공유를 자유롭게 설계할 수 있다 (이게 LangGraph 를 쓰는 이유).

그래프:
    START → supervisor ──(research)──▶ research ─┐
              ▲   │   ──(math)──────▶ math ───────┤
              └───┴─────────────────────────────── ┘  (worker 끝나면 supervisor 로 복귀)
                  └──(FINISH)──▶ END
"""

from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── worker 에이전트 2명 (각자 도구 보유) ───────────────────
@tool
def lookup_population(country: str) -> str:
    """국가 인구(백만 명)를 조회한다. 예: '대한민국', '일본', '미국'"""
    table = {"대한민국": 51, "일본": 124, "미국": 335}

    alias = {"한국": "대한민국", "korea": "대한민국", "south korea": "대한민국",
             "japan": "일본", "usa": "미국", "us": "미국", "united states": "미국"}
    
    key = alias.get(country.strip().lower(), country.strip())
    if key in table:
        return f"{key} 인구: {table[key]}백만 명"
    return f"{country}: 정보 없음"


@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


research_agent = create_agent(
    llm, 
    [lookup_population],
    system_prompt="lookup_population 도구로 조회해 수치를 간결히 보고하라.")

math_agent = create_agent(
    llm, 
    [calculator],
    system_prompt="대화에 이미 나온 수치만 써서 calculator 로 계산하라. 없는 값은 추정하지 말 것.")


# ─── 그래프 공유 상태 ───────────────────────────────────────
class State(TypedDict):
    messages: Annotated[list, add_messages]   # 노드들이 메시지를 누적 (reducer)
    next: str                                 # supervisor 의 라우팅 결정


# ─── supervisor 노드: 다음에 누구를 부를지(또는 종료) 결정 ──
class Route(TypedDict):
    next: Literal["research", "math", "FINISH"]


def supervisor(state: State) -> dict:
    sys = ("너는 팀 관리자다. 절대 네 지식으로 답하지 말고 반드시 담당에게 시킨다.\n"
           "- 필요한 수치(인구 등)가 아직 대화에 없으면 → research\n"
           "- 필요한 수치가 모두 나왔고 계산이 남았으면 → math\n"
           "- 계산까지 끝나 사용자에게 답할 수 있으면 → FINISH")

    decision = llm.with_structured_output(Route).invoke([("system", sys), *state["messages"]])

    # gpt-4o-mini 는 종료 시점에 빈 결정을 줄 때가 있음 → 더 시킬 일 없음 = FINISH 로 간주
    nxt = decision.get("next", "FINISH")
    print(f"  [supervisor] → {nxt}")
    return {"next": nxt}


# ─── worker 노드들 (각자 sub-agent 에게 위임) ───────────────
def research_node(state: State) -> dict:
    r = research_agent.invoke({"messages": state["messages"]})
    return {"messages": [("ai", "[research] " + r["messages"][-1].content)]}


def math_node(state: State) -> dict:
    r = math_agent.invoke({"messages": state["messages"]})
    return {"messages": [("ai", "[math] " + r["messages"][-1].content)]}


# ─── 그래프 조립 (노드 + 엣지 + START/END) ─────────────────
g = StateGraph(State)
g.add_node("supervisor", supervisor)
g.add_node("research", research_node)
g.add_node("math", math_node)

g.add_edge(START, "supervisor")                       # 시작은 항상 supervisor
g.add_conditional_edges(                              # supervisor 의 next 값으로 분기
    "supervisor",
    lambda s: s["next"],
    {"research": "research", "math": "math", "FINISH": END},
)
g.add_edge("research", "supervisor")                  # worker 끝나면 supervisor 로 복귀
g.add_edge("math", "supervisor")

app = g.compile()


# ─── 실행 ───────────────────────────────────────────────────
q = "대한민국과 일본 인구를 합치면 몇 백만 명이야?"
print(f"Q: {q}\n")
result = app.invoke({"messages": [("user", q)]}, config={"recursion_limit": 12})

print("\n=== 대화 흐름 ===")
for m in result["messages"]:
    tag = {"human": "사용자", "ai": "AI"}.get(m.type, m.type)
    print(f"  [{tag}] {m.content}")


# 정리:
#   - StateGraph 로 supervisor(라우터) ↔ worker 들을 노드·엣지로 직접 연결
#   - add_conditional_edges 로 supervisor 의 결정에 따라 분기 (research / math / END)
#   - worker → supervisor 엣지로 '루프' 형성 → 여러 단계 작업을 순차 처리
#   - recursion_limit 으로 루프 상한 (4.internals/4.3 참고)
#   - 병렬(여러 worker 동시) 이 필요하면 → 10.3_finance_analyst (fan-out/fan-in)
