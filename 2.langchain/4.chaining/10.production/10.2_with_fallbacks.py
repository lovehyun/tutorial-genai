"""
.with_fallbacks() — 주 체인 실패 시 백업 체인으로 폴백

운영 환경에서 모델 장애·rate limit 등을 대비해 백업 체인을 미리 정의해둡니다.
주 체인이 예외를 던지면 자동으로 백업 체인이 실행됩니다.

여기서는 일부러 실패하는 체인을 만들어 폴백 동작을 보여줍니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# 1) 일부러 실패하는 주 체인 (시뮬레이션용)
def always_fail(_):
    raise RuntimeError("주 체인 실패 시뮬레이션")

primary_chain = (
    ChatPromptTemplate.from_template("{question}")
    | llm
    | StrOutputParser()
    | RunnableLambda(always_fail)
)

# 2) 백업 체인 (정상 동작)
backup_chain = (
    ChatPromptTemplate.from_template("[백업 응답] {question} 에 대해 짧게 답해.")
    | llm
    | StrOutputParser()
)

# 3) 최후의 폴백 (LLM 자체가 죽었을 때 등)
last_resort = RunnableLambda(lambda _: "⚠️ 지금은 처리할 수 없습니다. 잠시 후 다시 시도해주세요.")

# 폴백 체이닝: primary → 실패 시 backup → 그래도 실패 시 last_resort
chain = primary_chain.with_fallbacks([backup_chain, last_resort])

result = chain.invoke({"question": "리스트가 뭐야?"})
print(result)
