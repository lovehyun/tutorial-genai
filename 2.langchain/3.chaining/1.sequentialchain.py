from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# OpenAI 모델 생성
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)

# 1단계: 회사명 생성
prompt1 = PromptTemplate(
    input_variables=["product"],
    template="You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
)

# 2단계: 회사 캐치프레이즈 생성
prompt2 = PromptTemplate(
    input_variables=["company_name"],
    template="Write a catch phrase for the following company: {company_name}"
)

# 최신 LangChain 방식 적용 (RunnableSequence)
chain = (
    prompt1 | llm | RunnableLambda(lambda x: {"company_name": x.strip()}) |
    prompt2 | llm | RunnableLambda(lambda x: {"catch_phrase": x.strip()})
)

# 실행
result = chain.invoke({"product": "웹게임"})
print(result["catch_phrase"])
