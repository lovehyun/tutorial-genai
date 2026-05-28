"""
.invoke() / .stream() / .batch() — 같은 체인의 세 가지 호출 방식

  - invoke(input)            : 입력 1개 → 출력 1개 (가장 기본)
  - stream(input)            : 입력 1개 → 토큰 단위 스트림 (챗봇 UX)
  - batch([in1, in2, ...])   : 입력 N개 → 출력 N개 (내부 병렬)

체인의 인터페이스는 동일하므로 세 메서드 모두 호출 가능합니다.
"""

import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_template("{question} 한 줄로 답해줘.")
chain = prompt | llm | StrOutputParser()


# (1) invoke
print("=" * 60)
print("(1) .invoke()")
print("=" * 60)
t0 = time.time()
print(chain.invoke({"question": "파이썬 리스트가 뭐야?"}))
print(f"소요: {time.time()-t0:.2f}s")


# (2) stream — 토큰이 생성되는 대로 받기
print("\n" + "=" * 60)
print("(2) .stream()")
print("=" * 60)
t0 = time.time()
for chunk in chain.stream({"question": "파이썬 딕셔너리가 뭐야?"}):
    print(chunk, end="", flush=True)
print(f"\n소요: {time.time()-t0:.2f}s")


# (3) batch — 여러 입력 병렬 처리
print("\n" + "=" * 60)
print("(3) .batch()")
print("=" * 60)
inputs = [
    {"question": "리스트가 뭐야?"},
    {"question": "딕셔너리가 뭐야?"},
    {"question": "튜플이 뭐야?"},
]
t0 = time.time()
results = chain.batch(inputs)
for i, r in enumerate(results, 1):
    print(f"[{i}] {r}")
print(f"소요: {time.time()-t0:.2f}s ({len(inputs)}건 병렬)")
