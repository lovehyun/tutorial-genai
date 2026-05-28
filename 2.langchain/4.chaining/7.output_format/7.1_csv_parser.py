"""
CommaSeparatedListOutputParser — 쉼표 구분 출력을 리스트로

LLM 에게 "쉼표로 구분해서 답해" 라고 시키고,
응답 문자열을 자동으로 파이썬 list 로 변환합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

parser = CommaSeparatedListOutputParser()

# 파서가 LLM 에게 줄 포맷 지시문 (예: "Return a comma separated list ...")
format_instructions = parser.get_format_instructions()

prompt = ChatPromptTemplate.from_template(
    "다음 주제와 관련된 키워드 5개를 알려줘.\n주제: {topic}\n\n{format_instructions}"
).partial(format_instructions=format_instructions)

chain = prompt | llm | parser

result = chain.invoke({"topic": "인공지능"})
print(type(result))   # <class 'list'>
print(result)         # ['머신러닝', '딥러닝', ...]
