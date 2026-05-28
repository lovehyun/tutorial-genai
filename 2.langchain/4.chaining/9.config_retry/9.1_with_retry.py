"""
.with_retry() — 일시적 실패에 대한 자동 재시도

네트워크 오류, 일시적 rate limit 등 일시적 실패를 LCEL 빌트인으로 처리합니다.
try/except 와 time.sleep 으로 짤 필요 없습니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_template("{question} 한 줄로 답해.")
chain = prompt | llm | StrOutputParser()

# 기존 chain 을 감싸기만 하면 끝
chain_with_retry = chain.with_retry(
    stop_after_attempt=3,           # 최대 3회 시도
    wait_exponential_jitter=True,   # 지수 백오프 + 랜덤 지터
    # retry_if_exception_type=(SomeError,)   # 특정 예외에만 재시도
)

result = chain_with_retry.invoke({"question": "리스트가 뭐야?"})
print(result)
