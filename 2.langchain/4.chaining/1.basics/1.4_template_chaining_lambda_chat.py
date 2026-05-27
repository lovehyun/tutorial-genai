from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Chat 버전: LCEL 체인에 RunnableLambda 끼우기

load_dotenv()

# 1. 프롬프트 템플릿 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "What is a good name for a {company} that makes {product}?"),
])

# 2. ChatOpenAI 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. 체인 구성 (프롬프트 → LLM → StrOutputParser → RunnableLambda 로 dict 화)
# chat 모델은 AIMessage 를 반환하므로 StrOutputParser 로 문자열로 먼저 변환한 뒤 lambda 에 넘긴다.
chain = prompt | llm | StrOutputParser() | RunnableLambda(lambda x: {"response": x.strip()})

# 4. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 5. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 6. 출력
print("\nFinal Response:")
print(result["response"])
