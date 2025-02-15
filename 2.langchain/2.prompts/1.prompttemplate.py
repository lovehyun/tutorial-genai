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

# 2. OpenAI 모델 생성 및 연동
llm = OpenAI(temperature=0.9)

# 3. 최신 LangChain 방식 적용 (RunnableSequence)
chain = prompt | llm | RunnableLambda(lambda x: {"response": x.strip()})

# 4. 모델 실행
result = chain.invoke({"company": "High Tech Startup", "product": "Web Game"})
print(result["response"])
