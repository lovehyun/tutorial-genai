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


# OpenAI 모델 생성
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.9)

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

# 따옴표와 줄바꿈 제거 함수
def clean_text(text):
    # 앞뒤 공백, 줄바꿈 제거
    text = text.strip()
    # 앞뒤 따옴표 제거 (있는 경우)
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()
    return text

# 3. LangChain 체인 구성
chain = (
    {"product": lambda x: x["product"]}
    | RunnablePassthrough.assign(
        company_name=lambda x: clean_text(llm.invoke(prompt1.format(product=x["product"])))
    )
    | RunnablePassthrough.assign(
        catch_phrase=lambda x: clean_text(llm.invoke(prompt2.format(company_name=x["company_name"])))
    )
)

# 4. 입력값 넣고 실행
input = {"product": "웹게임"}
result = chain.invoke(input)

# 5. 결과 출력
print("회사명:", result["company_name"])
print("캐치프레이즈:", result["catch_phrase"])
