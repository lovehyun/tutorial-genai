"""
RunnablePassthrough — 입력을 그대로 흘려보내며 .assign() 으로 새 키를 덧붙이는 Runnable.
이 예제: {"product": ...} 를 유지한 채 .assign() 한 번으로 company_name 키를 추가합니다.

dict 를 흘려보내며 새 키를 하나씩 붙입니다.
RunnableLambda 와의 차이: 기존 값을 잃지 않고 그대로 통과시킴.
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

# 입력 {"product": ...} 을 그대로 두면서 company_name 키 추가
chain = RunnablePassthrough.assign(
    company_name=lambda x: name_chain.invoke({"product": x["product"]}).strip()
)

result = chain.invoke({"product": "웹게임"})
print(result)
# {'product': '웹게임', 'company_name': '...'}  ← 둘 다 살아있음
