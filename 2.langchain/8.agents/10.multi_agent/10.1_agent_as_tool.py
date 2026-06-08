"""
멀티 에이전트 (1) — 에이전트를 '도구' 로 감싸기 (가장 단순한 위임).
이 예제: 메인 에이전트가 전문 에이전트(서브 에이전트)를 도구처럼 호출해 일을 넘긴다.

왜 한 에이전트로 다 안 하고 나누나?
  - 도구가 많아지면(>10) 라우팅 정확도 ↓, 토큰 ↑ (README FAQ 참고)
  - 도메인별로 system_prompt / 도구 세트를 따로 두면 각자 더 정확
  - 서브 에이전트는 '블랙박스 도구' 처럼 보이므로 메인은 결과만 받으면 됨

구조:
  메인 에이전트
    └─ ask_math_expert (도구) ── 호출 ──▶ 수학 전문 에이전트 (calculator 보유)

  ※ create_agent 자체가 이미 LangGraph 그래프(START→model→tools→END)다.
    여기선 그 '완성된 그래프' 를 도구처럼 재사용하는 가장 단순한 방법일 뿐,
    그래프(노드/엣지/START/END)를 '직접' 손으로 짜는 건 10.2 / 10.3 에서 한다.
    → 흐름 제어(병렬·반복·조건분기)가 필요하면 StateGraph 로 가야 한다.
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── 서브 에이전트: 수학 전문가 ─────────────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: '53 * 7 + 2'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


math_agent = create_agent(
    llm,
    [calculator],
    system_prompt="너는 수학 전문가다. 단계적으로 계산하고 최종 숫자만 명확히 답하라.",
)


# ─── 그 서브 에이전트를 '도구' 로 포장 ──────────────────────
@tool
def ask_math_expert(question: str) -> str:
    """복잡한 수학/계산 문제를 수학 전문 에이전트에게 위임하고 답을 받아온다."""
    result = math_agent.invoke({"messages": [("user", question)]})
    return result["messages"][-1].content


# ─── 메인 에이전트: 위임 도구 + 일반 대화 ───────────────────
main_agent = create_agent(
    llm,
    [ask_math_expert],
    system_prompt="너는 비서다. 계산이 필요한 부분은 ask_math_expert 에게 맡기고, "
                  "그 외에는 직접 답하라.",
)


def run(q: str):
    print(f"\nQ: {q}")
    result = main_agent.invoke({"messages": [("user", q)]})
    
    # 메인이 서브를 호출했는지 흔적 출력
    for m in result["messages"]:
        for c in getattr(m, "tool_calls", []) or []:
            print(f"  └─ 위임: {c['name']}({c['args']})")
    print(f"A: {result['messages'][-1].content}")


run("안녕? 너 누구야?")                              # 위임 없이 직접 답
run("어떤 카페 3곳 비용이 4500, 5200, 3800원이야. 총합과 평균은?")  # 수학 전문가에게 위임


# 정리:
#   - 서브 에이전트를 @tool 안에서 invoke → 메인은 그냥 '도구' 로 인식 (구조가 코드에 안 보임)
#   - 흐름 제어(여러 worker 병렬/반복/조건분기)가 필요하면 StateGraph → 10.2_supervisor / 10.3
#   - 단점: 호출이 중첩되어 토큰/지연 ↑. 정말 분리가 이득일 때만 나눌 것
