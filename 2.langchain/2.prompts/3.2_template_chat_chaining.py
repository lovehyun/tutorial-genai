import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. 메시지 기반 프롬프트 템플릿
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a naming consultant for new companies."),
#     ("human", "What is a good name for a {company} that makes {product}?")
# ])
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are a naming consultant for new companies"),
    HumanMessagePromptTemplate.from_template("What is a good name for a {company} that makes {product}?")
])

# 2. Chat LLM 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)

# 3. 후처리 함수
parser = StrOutputParser()

# 3-2. 후처리 함수 (AIMessage 객체의 .content 접근)
def debug_response(message):
    print("\nRaw Chat Output:")
    print(message)
    cleaned = message.content.strip().strip('"').strip()
    return {"response": cleaned}

# 4. 체인 구성 (프롬프트 → ChatLLM → 후처리)
# chain = prompt | llm | parser
# chain = prompt | llm | RunnableLambda(debug_response)
# 또는 간단히 문자열로 받을 때:
chain = prompt | llm | StrOutputParser() | RunnableLambda(lambda x: {"response": x})


# 5. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 5-2. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs) # inputs 는 원래 dict로 받을 수 있음

# 8. 출력
print("\nFinal Response:")
print(result["response"])
