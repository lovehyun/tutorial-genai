"""
RunnableMap — 입력 dict 를 키별 처리로 재구성하는 Runnable (RunnableParallel 별칭).
이 예제: 성+이름 → name, 생년-현재년 → age 처럼 여러 필드를 계산·결합해 새 dict 를 만듭니다.

호출하는 쪽의 dict 구조와 하위 체인이 기대하는 dict 구조가 다를 때,
RunnableMap 으로 변환합니다. 단순한 키 이름 매핑을 넘어 계산/결합도 가능.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

# 하위 체인: {name, age} 를 기대
intro_prompt = ChatPromptTemplate.from_template(
    "{name}({age}살)을 한 문장으로 소개해줘."
)
intro_chain = intro_prompt | llm | StrOutputParser()

# 호출하는 쪽은 first_name / last_name / birth_year / current_year 로 넘긴다고 가정
# → RunnableMap 으로 가공
prepare = RunnableMap({
    "name": lambda x: f"{x['last_name']}{x['first_name']}",     # 성+이름 합치기
    "age":  lambda x: x["current_year"] - x["birth_year"],     # 나이 계산
})

chain = prepare | intro_chain

result = chain.invoke({
    "first_name":   "수현",
    "last_name":    "박",
    "birth_year":   1990,
    "current_year": 2026,
})
print(result)
