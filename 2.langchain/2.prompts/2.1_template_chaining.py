from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# 1. 프롬프트 템플릿 설정
template = "You are a naming consultant for new companies. What is a good name for a {company} that makes {product}?"
prompt = PromptTemplate(
    input_variables=["company", "product"],
    template=template
)

# 2. OpenAI LLM 모델 정의
llm = OpenAI(temperature=0.9) # temperature=0.9로 설정되어 있어 창의적인 결과를 유도함
# llm = OpenAI(model="gpt-4o-mini", temperature=0.7) 

# 3. 출력 파서 정의
parser = StrOutputParser()

# 4. 체인 구성 (프롬프트 → LLM → 후처리) 을 보통 먼저...
# Runnable Composition (체이너블 객체 조합)
# | 연산자 기반의 체이닝 문법은 LangChain Expression Language (LCEL) 라고 불립니다.
chain = prompt | llm | parser

# 5. 입력 예제
inputs = {"company": "High Tech Startup", "product": "Web Game"}

# 6. 실행
print("Invoking chain with inputs:", inputs)
result = chain.invoke(inputs)

# 7. 출력
print("\nFinal Response:")
print(result)
