from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# ============================================================
# [0] 환경 준비
# ============================================================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY is not set")

# ============================================================
# [1] LLM (Chat) 설정
#   - gpt-4o-mini: 가볍고 빠른 최신 모델
#   - temperature: 0.7 정도로 이름/슬로건 다양성 확보
# ============================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
to_str = StrOutputParser()  # 문자열로 정돈

# ============================================================
# [2] 회사명 생성 체인
#   - product를 입력받아 회사명을 제안
#   - 한국어로 답하도록 명시
# ============================================================
name_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 전문 작명 컨설턴트입니다. 회사 이름을 창의적으로 제안하세요."),
    ("human", "다음 제품/서비스를 만드는 회사명을 1개 제안해줘. 제품: {product}")
])
name_chain = name_prompt | llm | to_str

# ============================================================
# [3] 캐치프레이즈 생성 체인
#   - company_name을 입력받아 슬로건 생성
# ============================================================
slogan_prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 브랜드 카피라이터입니다. 간결하고 임팩트 있는 한국어 슬로건을 작성하세요."),
    ("human", "회사명: {company_name}\n이 회사에 어울리는 캐치프레이즈를 1개 작성해줘.")
])
slogan_chain = slogan_prompt | llm | to_str

# ============================================================
# [4] 파이프라인 조립
#   - 먼저 회사명 생성 → 그 결과를 슬로건 체인에 주입
#   - 최종 출력에는 회사명과 캐치프레이즈 둘 다 포함
# ============================================================
def make_slogan_inputs(company_name: str):
    return {"company_name": company_name}

pipeline = (
    # (A) 제품을 받아 회사명 생성
    name_chain
    # (B) 회사명을 dict로 감싸서 다음 체인 입력 구성
    | RunnableLambda(lambda company_name: {
        "company_name": company_name,
        "slogan_inputs": make_slogan_inputs(company_name)
    })
    # (C) 슬로건 체인 실행 → 결과 병합
    | RunnableLambda(lambda d: {
        "company_name": d["company_name"],
        "catch_phrase": slogan_chain.invoke(d["slogan_inputs"])
    })
)

# ============================================================
# [5] 실행
# ============================================================
inputs = {"product": "웹게임"}
result = pipeline.invoke(inputs)

print("회사명:", result["company_name"])
print("캐치프레이즈:", result["catch_phrase"])
