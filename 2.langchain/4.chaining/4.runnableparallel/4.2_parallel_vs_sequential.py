"""
RunnableParallel — 같은 입력을 여러 체인에 동시 실행하는 Runnable.
이 예제: 3개 체인을 순차 invoke 와 RunnableParallel 로 호출했을 때의 소요 시간을 비교합니다.

같은 3개 체인을 순차로 돌릴 때와 RunnableParallel 로 묶을 때의 소요 시간을 비교합니다.
LLM 호출은 대부분 네트워크 I/O 대기이므로 병렬화 효과가 큽니다.
"""

from time import perf_counter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

ko_chain = ChatPromptTemplate.from_template("다음을 한국어로 번역해줘: {text}") | llm | StrOutputParser()
ja_chain = ChatPromptTemplate.from_template("다음을 일본어로 번역해줘: {text}") | llm | StrOutputParser()
fr_chain = ChatPromptTemplate.from_template("다음을 프랑스어로 번역해줘: {text}") | llm | StrOutputParser()

inputs = {"text": "Hello, nice to meet you."}

# 1) 순차 실행
t0 = perf_counter()
ko = ko_chain.invoke(inputs)
ja = ja_chain.invoke(inputs)
fr = fr_chain.invoke(inputs)
sequential = perf_counter() - t0
print(f"[순차]  {sequential:.2f}s")

# 2) 병렬 실행 (RunnableParallel)
parallel_chain = RunnableParallel({"ko": ko_chain, "ja": ja_chain, "fr": fr_chain})

t0 = perf_counter()
result = parallel_chain.invoke(inputs)
parallel = perf_counter() - t0
print(f"[병렬]  {parallel:.2f}s")

print(f"\n가속비: x{sequential / parallel:.2f}")
