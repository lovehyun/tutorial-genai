"""
.invoke() vs .stream() vs .batch() — LCEL Runnable 의 세 가지 호출 방식

같은 체인에 대해 세 방식을 비교한다:
  - invoke(input)            : 입력 하나 → 출력 하나 (가장 기본)
  - stream(input)            : 입력 하나 → 토큰 단위 스트림 (챗봇 UX)
  - batch([input1, input2])  : 입력 여러 개 → 출력 여러 개 (병렬 처리)

체인의 인터페이스는 동일하다 (.invoke / .stream / .batch 다 사용 가능).
"""

import time
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
# (1) .invoke() — 가장 기본. 입력 하나 → 출력 하나
# ============================================================
print("=" * 60)
print("(1) .invoke() — 입력 하나 받아 결과 한 번에 반환")
print("=" * 60)
t0 = time.time()
result = chain.invoke({"question": "파이썬 리스트가 뭐야? 한 줄로 답해."})
print(f"결과: {result}")
print(f"소요: {time.time()-t0:.2f}s")


# ============================================================
# (2) .stream() — 토큰 단위 출력 (챗봇 UX)
# ============================================================
print("\n" + "=" * 60)
print("(2) .stream() — 토큰이 생성되는 대로 즉시 받기")
print("=" * 60)
t0 = time.time()
print("결과: ", end="", flush=True)
for chunk in chain.stream({"question": "파이썬 딕셔너리가 뭐야? 한 줄로 답해."}):
    print(chunk, end="", flush=True)
print(f"\n소요: {time.time()-t0:.2f}s   (생성 시작까지 더 빠르게 반응함)")


# ============================================================
# (3) .batch() — 여러 입력을 동시에 처리 (병렬)
# ============================================================
print("\n" + "=" * 60)
print("(3) .batch() — 여러 입력을 병렬로 처리해 한꺼번에 결과 반환")
print("=" * 60)
inputs = [
    {"question": "리스트가 뭐야? 한 줄로."},
    {"question": "딕셔너리가 뭐야? 한 줄로."},
    {"question": "튜플이 뭐야? 한 줄로."},
    {"question": "셋(set)이 뭐야? 한 줄로."},
]
t0 = time.time()
results = chain.batch(inputs)        # ← 내부적으로 병렬 호출
elapsed_batch = time.time() - t0
for i, r in enumerate(results):
    print(f"[{i+1}] {r}")
print(f"소요: {elapsed_batch:.2f}s   ({len(inputs)}건 병렬 처리)")


# ─── 참고: invoke 를 4번 순차로 했을 때와 비교 ───
print("\n" + "-" * 60)
print("[참고] 같은 4건을 invoke 로 순차 처리하면?")
print("-" * 60)
t0 = time.time()
for inp in inputs:
    chain.invoke(inp)
elapsed_seq = time.time() - t0
print(f"순차: {elapsed_seq:.2f}s   vs   배치: {elapsed_batch:.2f}s")
print(f"배치가 약 {elapsed_seq/elapsed_batch:.1f}배 빠름")
