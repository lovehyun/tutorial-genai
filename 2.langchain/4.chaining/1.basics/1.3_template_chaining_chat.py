from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Chat 버전: LCEL 파이프(|) 체이닝 — prompt | llm | parser

load_dotenv()

# 1. 프롬프트 템플릿 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "What is a good name for a {company} that makes {product}?"),
])

# 2. ChatOpenAI 모델 정의
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

# 3. 출력 파서 — chat 모델 결과(AIMessage) 를 그냥 문자열로 꺼냄
parser = StrOutputParser()

# 4. 체인 구성 (프롬프트 → LLM → 후처리)
# Runnable Composition (체이너블 객체 조합)
# "|" 연산자 기반의 체이닝 문법 = LangChain Expression Language (LCEL)
chain = prompt | llm | parser

# 5. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 6. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 7. 출력
print("\nFinal Response:")
print(result)
