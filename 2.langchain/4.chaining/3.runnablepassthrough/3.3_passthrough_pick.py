"""
RunnablePassthrough — 입력을 흘리며 .assign() 으로 키 추가 / .pick() 으로 추출하는 Runnable.
이 예제: .assign() 으로 누적된 dict 에서 필요한 키만 .pick() 으로 골라냅니다 (list/str 인자 차이).

체인 중간에 .assign() 으로 키가 계속 쌓이지만,
최종적으로는 일부 키만 필요할 때 .pick() 으로 깔끔하게 골라냅니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

name_chain   = ChatPromptTemplate.from_template("{product} 회사명을 1개, 이름만.") | llm | StrOutputParser()
slogan_chain = ChatPromptTemplate.from_template("'{company_name}' 회사의 슬로건 한 줄.") | llm | StrOutputParser()

# 전체 체인: product / company_name / catch_phrase 모두 들고 있음
full_chain = (
    RunnablePassthrough.assign(company_name=lambda x: name_chain.invoke(x).strip())
    | RunnablePassthrough.assign(catch_phrase=lambda x: slogan_chain.invoke(x).strip())
)

print("[전체 dict — 누적된 모든 키]")
print(full_chain.invoke({"product": "웹게임"}))


# .pick() — 리스트로 주면 dict 그대로, 단일 문자열로 주면 값 자체만 반환
pick_two   = full_chain | RunnablePassthrough.pick(["company_name", "catch_phrase"])
pick_one   = full_chain | RunnablePassthrough.pick("catch_phrase")

print("\n[리스트로 pick — dict 유지]")
print(pick_two.invoke({"product": "웹게임"}))

print("\n[문자열로 pick — 값 자체]")
print(pick_one.invoke({"product": "웹게임"}))
