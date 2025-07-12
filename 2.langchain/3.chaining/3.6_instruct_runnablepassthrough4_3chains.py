from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# 환경 변수 로드 (경로 없이 실행하면 자동으로 .env 검색)
load_dotenv()

# input: "웹게임"
# ↓
# prompt1: "웹게임을 만드는 회사명을 지어줘"
# → "Playverse"
# prompt2: "Playverse에 어울리는 캐치프레이즈는?"
# → "Unleash the fun. Rule the game."
# prompt3: "해당 기업에 어울리는 소개/홍보 문구?"
# → "xxxxx"

# OpenAI 모델 생성
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9, max_tokens=1000)

# 1. 제품 기반으로 회사명 생성
prompt1 = PromptTemplate(
    input_variables=["product"],
    template="You are a naming consultant for new companies. What is a good name for a company that makes {product}?"
)

# 2. 회사명 기반으로 슬로건(캐치프레이즈) 생성
prompt2 = PromptTemplate(
    input_variables=["company_name"],
    template="Write a catch phrase for the following company: {company_name}"
)

# 3. 회사 소개 홍보문구 생성
prompt3 = PromptTemplate(
    input_variables=["company_name", "catch_phrase"],
    template=(
        "Write a promotional paragraph for a company named {company_name} "
        "with the catch phrase \"{catch_phrase}\". The paragraph should describe the company's vision, "
        "what it offers, and why customers should care."
    )
)

# 4. LangChain 방식 적용
# 전체 체인: 회사명 보존하면서 캐치프레이즈 추가
chain = (
    {"product": lambda x: x["product"]}  # 입력 데이터 시작
    | RunnablePassthrough.assign(
        company_name=lambda x: llm.invoke(prompt1.format(product=x["product"])).strip()
    )
    | RunnablePassthrough.assign(
        catch_phrase=lambda x: llm.invoke(prompt2.format(company_name=x["company_name"])).strip()
    )
    | RunnablePassthrough.assign(
        promo_paragraph=lambda x: llm.invoke(
            prompt3.format(
                company_name=x["company_name"],
                catch_phrase=x["catch_phrase"]
            ), config={""}
        ).strip()
    )
)

# RunnablePassthrough는 입력 데이터를 변형 없이 통과시키면서 동시에 추가 작업을 수행할 수 있게 해주는 특별한 컴포넌트입니다. 
# RunnableLambda와의 주요 차이점은:
#  - 상태 유지: 기존 데이터를 유지하면서 새 필드를 추가할 수 있습니다.
#  - 데이터 보존: 체인의 이전 단계에서 생성된 데이터를 잃지 않고 보존합니다.


# 5. 입력값 넣고 실행
input = {"product": "웹게임"}
result = chain.invoke(input)

# 6. 결과 출력
print("회사명:", result["company_name"])
print("캐치프레이즈:", result["catch_phrase"])
print("[홍보 문구]\n", result["promo_paragraph"])
