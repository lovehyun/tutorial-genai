"""
가장 기본 LCEL 체인 — prompt | llm | parser

세 컴포넌트를 파이프(|)로 연결하면 하나의 Runnable 체인이 됩니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 어시스턴트입니다."),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"question": "파이썬이 뭐야? 한 줄로 답해줘."})
print(result)
