"""
.with_config() — 체인에 메타데이터(tags / run_name / metadata) 부착

LangSmith 같은 trace 도구에서 어떤 체인이 호출됐는지 검색·필터링할 때 사용합니다.
체인 동작 자체는 그대로이고, 메타데이터만 추가됩니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_template("{question} 한 줄로 답해.")
chain = prompt | llm | StrOutputParser()

# 동일 체인에 라벨/메타데이터/이름을 붙임
chain_tagged = chain.with_config({
    "tags":     ["production", "user-query"],
    "metadata": {"version": "v2", "experiment": "A"},
    "run_name": "ProductionUserQueryChain",
})

result = chain_tagged.invoke({"question": "딕셔너리가 뭐야?"})
print(result)
print("→ LangSmith 등 trace 도구에서 위 tags / metadata 로 필터링 가능")


# 조합: .with_retry() + .with_config() 같이 쓰기
chain_full = (
    chain
    .with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
    .with_config({"tags": ["resilient"], "run_name": "ResilientChain"})
)
print("\n[조합 예]", chain_full.invoke({"question": "튜플이 뭐야?"}))
