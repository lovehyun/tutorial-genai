"""
미들웨어 (3) — 나만의 미들웨어 작성 (AgentMiddleware 상속).
이 예제: 모델 호출 직전/직후에 끼어들어 로깅·집계를 한다 (before_model / after_model).

훅 (각각 dict 반환 시 상태 갱신, None 이면 변경 없음):
  - before_model(state, runtime): 모델 호출 '직전' — 입력 검사/로깅/상태 수정
  - after_model(state, runtime) : 모델 응답 '직후' — 출력 로깅/후처리
  - 그 외: wrap_model_call / wrap_tool_call / before_agent / after_agent
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware

load_dotenv()


# ─── 커스텀 미들웨어: 모델 호출 횟수·토큰을 직접 집계 ───────
class TraceMiddleware(AgentMiddleware):
    """내장 미들웨어로 부족할 때 — 직접 로깅/집계를 끼운다."""

    def __init__(self):
        super().__init__()
        self.calls = 0

    def before_model(self, state, runtime):
        self.calls += 1
        print(f"  [before_model] 호출 #{self.calls}, 누적 메시지 {len(state['messages'])}개")
        return None   # 상태 변경 없음

    def after_model(self, state, runtime):
        last = state["messages"][-1]
        u = getattr(last, "usage_metadata", None)
        if u:
            print(f"  [after_model ] 토큰 in={u['input_tokens']} out={u['output_tokens']}")
        return None


@tool
def calculator(expression: str) -> str:
    """수학 식을 계산한다."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"오류: {e}"


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tracer = TraceMiddleware()
agent = create_agent(llm, [calculator], middleware=[tracer])

result = agent.invoke({"messages": [("user", "(7 + 5) * 3 은?")]})
print(f"\n답변: {result['messages'][-1].content}")
print(f"총 모델 호출: {tracer.calls}회  (도구 호출 때문에 2회 이상)")


# 정리:
#   - AgentMiddleware 상속 → before_model / after_model / wrap_model_call / wrap_tool_call 오버라이드
#   - 내장 미들웨어(12.1 요약 / 12.2 PII / ToolRetry 등)로 부족할 때 직접 작성
#   - 데코레이터 형태도 가능: @before_model def f(state, runtime): ...
