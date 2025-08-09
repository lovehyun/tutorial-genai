from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
to_str = StrOutputParser()

# 1. 프롬프트 및 체인 구성
# 1-1. 회사명
name_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 작명 컨설턴트입니다. 한국어로 회사명을 1개, 따옴표 없이 한 줄로만 출력하세요."),
    ("human", "다음 제품/서비스를 만드는 회사명을 제안해줘. 제품: {product}")
])
name_chain = name_prompt | llm | to_str

# 1-2. 캐치프레이즈
slogan_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 카피라이터입니다. 한국어 캐치프레이즈를 1개, 따옴표 없이 한 줄로만 출력하세요."),
    ("human", "회사명: {company_name}\n이 회사에 어울리는 캐치프레이즈를 작성해줘.")
])
slogan_chain = slogan_prompt | llm | to_str

# 1-3. 홍보 문구
promo_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 마케팅 카피라이터입니다. 한 단락의 홍보 문구를 작성하세요."),
    ("human", "회사명: {company_name}\n캐치프레이즈: {catch_phrase}\n"
              "비전, 제공 가치, 왜 고객이 주목해야 하는지를 담아, 자연스러운 한국어로 3~5문장으로 작성해줘.")
])
promo_chain = promo_prompt | llm | to_str

# 2. 전체 체인 구성 (Passthrough로 상태 누적)
chain = (
    {"product": lambda x: x.get("product", "")}
    | RunnablePassthrough.assign(
        company_name=lambda x: name_chain.invoke({"product": x["product"]}).strip()
    )
    | RunnablePassthrough.assign(
        catch_phrase=lambda x: slogan_chain.invoke({"company_name": x["company_name"]}).strip()
    )
    | RunnablePassthrough.assign(
        promo_paragraph=lambda x: promo_chain.invoke({
            "company_name": x["company_name"],
            "catch_phrase": x["catch_phrase"]
        }).strip()
    )
)

# 3. 결과 출력
result = chain.invoke({"product": "웹게임"})
print(f"[회사명] : {result["company_name"]}\n")
print(f"[캐치프레이즈] : {result["catch_phrase"]}\n")
print(f"[홍보 문구]\n  {result["promo_paragraph"]}\n")
