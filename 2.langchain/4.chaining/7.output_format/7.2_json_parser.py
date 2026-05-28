"""
JsonOutputParser — JSON 문자열 출력을 dict 로

LLM 에게 "JSON 으로 답해" 라고 시키고,
응답을 자동으로 파이썬 dict 로 변환합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_template(
    "다음 회사의 소개 정보를 JSON 으로 만들어줘.\n"
    "회사명: {company}\n\n"
    '형식 예시: {{"name": "회사명", "industry": "산업", "slogan": "한 줄 슬로건"}}'
    "\n반드시 JSON 만 출력하세요."
)

chain = prompt | llm | parser

result = chain.invoke({"company": "테슬라"})
print(type(result))            # <class 'dict'>
print(result)
print("산업:", result.get("industry"))
print("슬로건:", result.get("slogan"))
