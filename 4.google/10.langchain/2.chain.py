# pip install langchain-google-genai langchain-core python-dotenv

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

# LCEL 체인 구성
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 {role} 전문가입니다. 쉽고 명확하게 설명해주세요."),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

# 실행
result = chain.invoke({
    "role": "데이터 사이언스",
    "question": "머신러닝과 딥러닝의 차이점은 무엇인가요?",
})
print(result)
