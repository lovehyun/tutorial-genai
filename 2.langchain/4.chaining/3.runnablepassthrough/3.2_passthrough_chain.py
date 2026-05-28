"""
RunnablePassthrough — 입력을 그대로 흘려보내며 .assign() 으로 새 키를 덧붙이는 Runnable.
이 예제: .assign() 을 두 번 이어 product → +company_name → +catch_phrase 로 dict 를 누적합니다.

product → company_name 추가 → catch_phrase 추가
각 단계 결과를 모두 보존하므로, 최종 결과에서 모든 중간값을 꺼내볼 수 있습니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

name_prompt = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 회사 이름을 1개만 추천해줘. 이름만 답해."
)
name_chain = name_prompt | llm | StrOutputParser()

slogan_prompt = ChatPromptTemplate.from_template(
    "'{company_name}' 회사의 슬로건을 한 줄로 만들어줘."
)
slogan_chain = slogan_prompt | llm | StrOutputParser()

chain = (
    RunnablePassthrough.assign(
        company_name=lambda x: name_chain.invoke({"product": x["product"]}).strip()
    )
    | RunnablePassthrough.assign(
        catch_phrase=lambda x: slogan_chain.invoke({"company_name": x["company_name"]}).strip()
    )
)

result = chain.invoke({"product": "웹게임"})
print(f"제품:     {result['product']}")
print(f"회사명:   {result['company_name']}")
print(f"슬로건:   {result['catch_phrase']}")
