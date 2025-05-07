from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# 1. 프롬프트 템플릿 설정
template = "You are a naming consultant for new companies. What is a good name for a {company} that makes {product}?"
prompt = PromptTemplate(
    input_variables=["company", "product"],
    template=template
)

# 2. OpenAI LLM 모델 생성 및 연동
llm = OpenAI(temperature=0.9) # temperature=0.9로 설정되어 있어 창의적인 결과를 유도함
# llm = OpenAI(model="gpt-4", temperature=0.7) 

# 3. 후처리 정의: 출력 문자열 로그 찍고 정리
def debug_response(output):
    print("\nRaw LLM Output:")
    print(output)
    # return {"response": output.strip()}
    cleaned = output.strip().strip('"').strip()  # 앞뒤 따옴표 및 추가 공백 제거
    return {"response": cleaned}

# 4. 체인 구성 (프롬프트 → LLM → 후처리)
chain = prompt | llm | RunnableLambda(debug_response)
# chain = prompt | llm | RunnableLambda(lambda x: {"response": x.strip()})

# 5. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 6. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 7. 출력
print("\nFinal Response:")
print(result["response"])
