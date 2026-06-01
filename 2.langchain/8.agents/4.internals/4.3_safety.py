"""
에이전트 안전장치 — 무한 루프 / 도구 폭주 방지.
이 예제: recursion_limit, 도구 실행 try/except, 입력 검증 등 운영 필수 패턴.

왜 필요한가?
  - LLM 이 같은 도구를 계속 부르며 루프에 빠질 수 있음 (특히 결과 해석 실패 시)
  - 도구 안에서 예외가 발생해도 에이전트는 그 자리에서 멈춤 → 사용자에게 raw traceback
  - 잘못된 인자 (eval 인젝션, 큰 입력 등) 가 들어오면 보안/성능 문제

세 가지 방어선:
  1) recursion_limit 으로 LLM ↔ 도구 호출 횟수 상한 강제
  2) 도구 함수 자체에 try/except 로 우아한 에러 메시지
  3) Pydantic args_schema 로 입력 검증 (2.custom_tools/2.3 참고)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent

load_dotenv()


# ─── 도구 내부에 안전장치 (try/except) ──────────────────────
@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 잘못된 식은 오류 메시지 반환."""
    # 입력 길이 제한
    if len(expression) > 100:
        return "오류: 식이 너무 깁니다 (최대 100자)"

    # eval 위험 차단 — 빌트인 차단
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"   # ← raw traceback 대신 깔끔한 문자열로


@tool
def flaky_api(query: str) -> str:
    """가끔 실패하는 외부 API 시뮬레이션."""
    import random
    if random.random() < 0.5:
        raise RuntimeError("API timeout")
    return f"결과: {query}"


# ─── recursion_limit — 호출 횟수 상한 ──────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [calculator, flaky_api])

config = {"recursion_limit": 10}   # ← 무한 루프 방지 (LangGraph 의 노드 호출 상한)


# ─── 1) 정상 동작 ──────────────────────────────────────────
print("=" * 60)
print("(1) 정상 호출 (recursion_limit=10)")
print("=" * 60)
result = agent.invoke({"messages": [("user", "15 * 24 는?")]}, config=config)
print(f"답변: {result['messages'][-1].content}\n")


# ─── 2) 잘못된 식 — 도구 안에서 우아하게 처리 ──────────────
print("=" * 60)
print("(2) 잘못된 식 — 도구 안에서 try/except 처리")
print("=" * 60)
result = agent.invoke({"messages": [("user", "'abc' + 5 는?")]}, config=config)
print(f"답변: {result['messages'][-1].content}\n")


# ─── 3) recursion 초과 시뮬레이션 ──────────────────────────
# recursion_limit 을 작게 잡고 의도적으로 루프가 길어지는 상황을 만들면
# GraphRecursionError 가 발생합니다. 운영에서는 try/except 로 잡아서
# "처리 시간 초과" 같은 메시지로 사용자에게 전달.
print("=" * 60)
print("(3) recursion_limit 초과 시 에러 처리")
print("=" * 60)
try:
    result = agent.invoke(
        {"messages": [("user", "flaky_api 를 'hello' 인자로 호출해줘.")]},
        config={"recursion_limit": 3},  # ← 일부러 작게
    )
    print(f"답변: {result['messages'][-1].content}")
except Exception as e:
    # GraphRecursionError 등을 사용자 친화 메시지로 변환
    print(f"[안전 처리] 너무 많은 시도로 중단: {type(e).__name__}")


# ─────────────────────────────────────────────────────────
# 실전 체크리스트:
#   ✓ recursion_limit 설정 (보통 10~25)
#   ✓ 도구 함수에 try/except + 의미있는 오류 메시지 반환
#   ✓ Pydantic args_schema 로 입력 검증 (2.custom_tools/2.3)
#   ✓ 위험한 도구 (송금/삭제 등) 는 interrupt_before 로 HITL (6.hitl_streaming/6.1)
#   ✓ LangSmith 같은 trace 도구로 운영 모니터링
# ─────────────────────────────────────────────────────────
