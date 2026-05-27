from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# Chat 버전: LCEL 체인에 커스텀 함수(디버그/후처리) 끼우기

load_dotenv()

# 1. 프롬프트 템플릿 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "What is a good name for a {company} that makes {product}?"),
])

# 2. ChatOpenAI 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. 후처리 함수 정의: 출력 문자열 로그 찍고 정리
def debug_response(output):
    print("\nRaw LLM Output:")
    print(output)
    # return {"response": output.strip()}
    # cleaned = output.strip().strip('"').strip()  # 앞뒤 따옴표 및 추가 공백 제거
    # cleaned = output.strip().replace('.')        # 문장 내의 . 제거
    cleaned = output.strip().split('.')[-1].strip()  # . 으로 나눠서 뒷부분만 유지
    return {"response": cleaned}

# 4. 체인 구성 (프롬프트 → LLM → StrOutputParser → 커스텀 함수)
# chat 모델은 AIMessage 를 반환하므로 StrOutputParser 로 문자열화한 뒤 커스텀 함수에 넘긴다.
chain = prompt | llm | StrOutputParser() | RunnableLambda(debug_response)

# 5. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 6. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 7. 출력
print("\nFinal Response:")
print(result["response"])
