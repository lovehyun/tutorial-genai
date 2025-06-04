import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# 1. 환경 변수 로드
load_dotenv()

# 2. 메시지 기반 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("human", "What is a good name for a {company} that makes {product}?")
])

# 3. Chat LLM 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9)

# 4. 후처리 함수 (AIMessage 객체의 .content 접근)
def debug_response(message):
    print("\nRaw Chat Output:")
    print(message)
    cleaned = message.content.strip().strip('"').strip()
    return {"response": cleaned}

# 5. 체인 구성 (프롬프트 → ChatLLM → 후처리)
# chain = prompt | llm | RunnableLambda(debug_response)
# 또는 간단히 문자열로 받을 때:
chain = prompt | llm | StrOutputParser() | RunnableLambda(lambda x: {"response": x})

# 6. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 7. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 8. 출력
print("\nFinal Response:")
print(result["response"])
