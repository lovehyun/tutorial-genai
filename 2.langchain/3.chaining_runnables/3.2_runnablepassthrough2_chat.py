import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# input: "웹게임"
# ↓
# prompt1: "웹게임을 만드는 회사명을 지어줘"
# → "Playverse"
# prompt2: "Playverse에 어울리는 캐치프레이즈는?"
# → "Unleash the fun. Rule the game."


# OpenAI 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

to_str = StrOutputParser()

# 1. 제품 기반 회사명 생성 프롬프트
# prompt1 = ChatPromptTemplate.from_messages([
#     HumanMessagePromptTemplate.from_template(
#         "You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
#     )
# ])
name_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 작명 컨설턴트입니다. 한국어로 회사명을 1개 제안하세요."),
    ("human", "다음 제품/서비스를 만드는 회사명을 1개 제안해줘. 제품: {product}")
])
name_chain = name_prompt | llm | to_str

# 2. 회사명 기반 슬로건 생성 프롬프트
# prompt2 = ChatPromptTemplate.from_messages([
#     HumanMessagePromptTemplate.from_template(
#         "Write a catch phrase for the following company: {company_name}"
#     )
# ])

slogan_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 카피라이터입니다. 간결한 한국어 캐치프레이즈를 1개 작성하세요."),
    ("human", "회사명: {company_name}\n이 회사에 어울리는 캐치프레이즈를 1개 작성해줘.")
])
slogan_chain = slogan_prompt | llm | to_str

# 3. LangChain 방식 적용
# 전체 체인: 회사명 보존하면서 캐치프레이즈 추가
chain = (
    {"product": lambda x: x["product"]}  # 입력 데이터 시작
    | RunnablePassthrough.assign(
        company_name=lambda x: name_chain.invoke({"product": x["product"]}).strip()
    )
    | RunnablePassthrough.assign(
        catch_phrase=lambda x: slogan_chain.invoke({"company_name": x["company_name"]}).strip()
    )
)

# RunnablePassthrough는 입력 데이터를 변형 없이 통과시키면서 동시에 추가 작업을 수행할 수 있게 해주는 특별한 컴포넌트입니다. 
# RunnableLambda와의 주요 차이점은:
#  - 상태 유지: 기존 데이터를 유지하면서 새 필드를 추가할 수 있습니다.
#  - 데이터 보존: 체인의 이전 단계에서 생성된 데이터를 잃지 않고 보존합니다.


# 4. 입력값 넣고 실행
inputs = {"product": "웹게임"}
result = chain.invoke(inputs)

# 5. 결과 출력
print("회사명:", result["company_name"])
print("캐치프레이즈:", result["catch_phrase"])


# 6. 필요시... 3번 뒤에 최종 클린업 체인 추가
# def clean_all(d):
#     for k in ("company_name", "catch_phrase"):
#         if k in d and isinstance(d[k], str):
#             d[k] = d[k].strip().strip('"').strip("'")
#     return d
#
# chain = chain | RunnableLambda(clean_all)
