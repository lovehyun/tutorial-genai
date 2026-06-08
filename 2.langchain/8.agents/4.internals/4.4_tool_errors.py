"""
도구 에러 처리 — 도구가 예외를 던지면? (3가지 대응)
이 예제: (A) 기본은 예외가 전파되어 중단, (B) 도구 내부 try/except 로 우아하게,
         (C) ToolRetryMiddleware 로 '일시 오류' 자동 재시도.

왜?
  - 외부 API 도구는 타임아웃/일시 오류가 흔함
  - 처리 안 하면 raw 예외로 에이전트가 멈춤 → 사용자에게 traceback
  - 영구 오류는 우아한 메시지로(B), 일시 오류는 자동 재시도(C)
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ─── (A) 기본: 도구가 raise → 예외가 그대로 전파되어 중단 ──
@tool
def broken_weather(city: str) -> str:
    """도시 날씨를 조회한다 (항상 실패하는 외부 API)."""
    raise RuntimeError("날씨 API 연결 실패")


print("=" * 60)
print("(A) 기본 — 도구 예외는 전파되어 에이전트가 중단됨")
print("=" * 60)
agent_a = create_agent(llm, [broken_weather])
try:
    agent_a.invoke({"messages": [("user", "서울 날씨 알려줘")]})
except Exception as e:
    print(f"[중단] 도구 예외가 그대로 전파됨 → {type(e).__name__}: {e}\n")


# ─── (B) 도구 내부 try/except → 에러를 '문자열'로 반환 ─────
# 모델이 에러 문자열을 받아서 "조회 실패"를 사용자에게 알릴 수 있음.
@tool
def safe_weather(city: str) -> str:
    """도시 날씨를 조회한다 (실패해도 우아하게 처리)."""
    try:
        raise RuntimeError("날씨 API 연결 실패")
    except Exception as e:
        return f"날씨 조회 실패: {e}"


print("=" * 60)
print("(B) 도구 내부 try/except — 에러를 문자열로 반환(모델이 처리)")
print("=" * 60)
agent_b = create_agent(llm, [safe_weather])
result = agent_b.invoke({"messages": [("user", "서울 날씨 알려줘")]})
print(f"최종 답변: {result['messages'][-1].content}\n")


# ─── (C) ToolRetryMiddleware: 일시 오류 자동 재시도 ────────
_attempts = {"n": 0}


@tool
def flaky_weather(city: str) -> str:
    """도시 날씨를 조회한다 (처음 2번 실패 후 성공하는 불안정 API)."""
    _attempts["n"] += 1
    if _attempts["n"] < 3:
        raise RuntimeError(f"일시 오류 (시도 {_attempts['n']})")
    return f"{city}: 맑음, 22도"


print("=" * 60)
print("(C) ToolRetryMiddleware — 일시 오류 자동 재시도(최대 3회)")
print("=" * 60)
agent_c = create_agent(
    llm,
    [flaky_weather],
    middleware=[ToolRetryMiddleware(max_retries=3, initial_delay=0.1, backoff_factor=1.0)],
)
result = agent_c.invoke({"messages": [("user", "서울 날씨 알려줘")]})
print(f"도구 호출 시도 횟수: {_attempts['n']}  (2번 실패 후 3번째 성공)")
print(f"최종 답변: {result['messages'][-1].content}")


# 정리:
#   - 기본은 도구 예외가 전파되어 '중단' → 반드시 처리 필요
#   - 영구 오류: 도구 내부 try/except 로 의미있는 문자열 반환 (4.3_safety 와 동일 패턴)
#   - 일시 오류: ToolRetryMiddleware(max_retries / retry_on / backoff_factor) 로 자동 재시도
