"""
RunnableLambda — 임의의 파이썬 함수를 체인 단계로 끼우는 Runnable.
이 예제: LLM 출력 str 을 dict 로 변환해서 다음 체인(슬로건 생성)에 연결합니다.

LLM 의 출력(str)을 다음 프롬프트가 받는 형식(dict)으로 변환해서 넘깁니다.
  product → 회사명(str) → {"company_name": ...} → 슬로건
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 체인 A: 제품 → 회사명
name_prompt = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사 이름을 1개만 추천해줘. 이름만 답해."
)
name_chain = name_prompt | llm | StrOutputParser()

# 체인 B: 회사명 → 슬로건
slogan_prompt = ChatPromptTemplate.from_template(
    "'{company_name}' 회사의 슬로건을 한 줄로 만들어줘."
)
slogan_chain = slogan_prompt | llm | StrOutputParser()

# A → (str을 dict로 변환) → B
pipeline = (
    name_chain
    | RunnableLambda(lambda name: {"company_name": name.strip()})
    | slogan_chain
)

result = pipeline.invoke({"product": "웹게임"})
print("슬로건:", result)
