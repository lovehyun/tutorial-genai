"""
.with_config() / .with_retry() — Runnable 의 메타 설정과 자동 재시도

LCEL 체인의 동작을 코드 거의 안 바꾸고 강화하는 두 메서드:

  - .with_retry()  : 실패 시 자동 재시도 (지수 백오프 / jitter 내장)
                     → 수동으로 try/except + time.sleep 짤 필요 없음
  - .with_config() : tags / metadata / run_name 등 trace·debug 메타데이터 부착
                     → LangSmith 같은 trace 도구에서 필터링/검색 용이
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 짧고 명료하게 답하는 어시스턴트입니다."),
    ("user",   "{question}"),
])
chain = prompt | llm | StrOutputParser()


# ============================================================
# (1) .with_retry() — 자동 재시도
# ============================================================
# 네트워크 오류, 일시적 rate limit 등 일시적 실패에 대응.
# 기존 chain 을 감싸기만 하면 됨.
chain_with_retry = chain.with_retry(
    stop_after_attempt=3,             # 최대 3회 시도
    wait_exponential_jitter=True,     # 지수 백오프 + 지터(랜덤 흔들기)
    # retry_if_exception_type=(SomeError,)   # 특정 예외만 재시도하고 싶다면
)

print("=" * 60)
print("(1) .with_retry() — 자동 재시도 (3회까지)")
print("=" * 60)
result = chain_with_retry.invoke({"question": "리스트가 뭐야? 한 줄로."})
print(f"결과: {result}")


# ============================================================
# (2) .with_config() — 메타데이터 부착 (trace·디버깅용)
# ============================================================
# LangSmith 같은 trace 도구에서 위 tags/metadata 로 필터링 가능.
# 운영 중 어떤 chain 이 호출됐는지 추적할 때 유용.
chain_tagged = chain.with_config({
    "tags":     ["production", "user-query"],
    "metadata": {"version": "v2", "experiment": "A"},
    "run_name": "ProductionUserQueryChain",
})

print("\n" + "=" * 60)
print("(2) .with_config() — tags / metadata / run_name 부착")
print("=" * 60)
result = chain_tagged.invoke({"question": "딕셔너리가 뭐야? 한 줄로."})
print(f"결과: {result}")
print("→ LangSmith 등 trace 도구에서 위 tags/metadata 로 필터링 가능")


# ============================================================
# (3) 조합 — with_retry + with_config 같이 사용
# ============================================================
# 두 메서드는 체이닝 가능. Runnable 을 점점 두텁게 감쌈.
chain_full = (
    chain
    .with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
    .with_config({"tags": ["resilient"], "run_name": "ResilientChain"})
)

print("\n" + "=" * 60)
print("(3) .with_retry() + .with_config() 조합")
print("=" * 60)
result = chain_full.invoke({"question": "튜플이 뭐야? 한 줄로."})
print(f"결과: {result}")


# ─── 비교: 수동 retry vs .with_retry() ────────────────────
# 수동 (7.production/10.1_production_fallback_retry.py 같은 패턴):
#   for attempt in range(3):
#       try:
#           return chain.invoke(...)
#       except SomeError:
#           time.sleep(2 ** attempt)
#
# LCEL 빌트인:
#   chain.with_retry(stop_after_attempt=3, wait_exponential_jitter=True).invoke(...)
#
# → 한 줄로 끝. 콜백/로깅도 LCEL trace 와 통합됨.
