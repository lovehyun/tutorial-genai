from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableLambda

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# input: "웹게임"
# ↓
# prompt1: "웹게임을 만드는 회사명을 지어줘"
# → "Playverse"
# prompt2: "Playverse에 어울리는 캐치프레이즈는?"
# → "Unleash the fun. Rule the game."


# OpenAI 모델 생성
llm = ChatOpenAI(model="gpt-4o", temperature=0.9)

# 1. 제품 기반으로 회사명 생성
prompt1 = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
    )
])

# 2. 회사명 기반으로 슬로건(캐치프레이즈) 생성
prompt2 = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(
        "Write a catch phrase for the following company: {company_name}"
    )
])

# 3. LangChain 방식 적용 (RunnableSequence)
chain = (
    prompt1 | llm | RunnableLambda(lambda x: {"company_name": x.strip()}) |
    prompt2 | llm | RunnableLambda(lambda x: {"catch_phrase": x.strip()})
)
# RunnableLambda는 단순히 사용자 정의 함수를 체인에 통합할 수 있게 해주는 래퍼입니다. 
# 입력을 받아 변환하고 출력을 다음 단계로 전달합니다. 
# 주로 데이터 형식을 변환하거나 추가 처리를 수행할 때 사용합니다.

# 4. 입력값 넣고 실행
input = {"product": "웹게임"}
result = chain.invoke(input)

# 5. 결과 출력
# print("회사명:", result["company_name"]) # 중간 결과는 못 가져옴
print("캐치프레이즈:", result["catch_phrase"])