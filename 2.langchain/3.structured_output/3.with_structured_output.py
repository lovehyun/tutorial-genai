"""
.with_structured_output() — 최신 구조화 출력 방식

ChatOpenAI의 .with_structured_output(PydanticModel)을 사용하면
별도의 파서 없이도 LLM이 직접 구조화된 객체를 반환합니다.
OpenAI의 Function Calling / Tool Use를 내부적으로 활용합니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()

# ===== 1. Pydantic 모델 정의 =====
class CompanyProfile(BaseModel):
    """회사 프로필"""
    name: str = Field(description="회사 이름")
    industry: str = Field(description="산업 분야")
    description: str = Field(description="회사 소개 (1~2문장)")
    strengths: list[str] = Field(description="핵심 강점 3가지")
    target_market: str = Field(description="주요 타겟 시장")


# ===== 2. .with_structured_output() 사용 =====
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 구조화된 출력을 위한 LLM 래퍼 생성
structured_llm = llm.with_structured_output(CompanyProfile)

prompt = ChatPromptTemplate.from_template(
    "{product}을(를) 만드는 가상의 스타트업 회사 프로필을 만들어주세요."
)

# ===== 3. 체인 구성 — PydanticOutputParser 불필요! =====
chain = prompt | structured_llm

# ===== 4. 실행 =====
products = ["AI 기반 교육 플랫폼", "전기 자전거", "친환경 화장품"]

for product in products:
    result = chain.invoke({"product": product})
    # result는 이미 CompanyProfile 객체
    print(f"회사: {result.name}")
    print(f"산업: {result.industry}")
    print(f"소개: {result.description}")
    print(f"강점: {result.strengths}")
    print(f"타겟: {result.target_market}")
    print()


# ===== 5. 다중 구조체 예시 =====
print("=" * 50)
print("다중 구조체 예시: 음식 레시피")
print("=" * 50)

class Ingredient(BaseModel):
    """재료"""
    name: str = Field(description="재료 이름")
    amount: str = Field(description="필요량")

class Recipe(BaseModel):
    """요리 레시피"""
    dish_name: str = Field(description="요리 이름")
    difficulty: str = Field(description="난이도: 쉬움, 보통, 어려움")
    cooking_time: str = Field(description="조리 시간")
    ingredients: list[Ingredient] = Field(description="필요한 재료 목록")
    steps: list[str] = Field(description="조리 단계")

structured_llm2 = llm.with_structured_output(Recipe)

prompt2 = ChatPromptTemplate.from_template(
    "{dish}의 간단한 레시피를 알려주세요."
)

chain2 = prompt2 | structured_llm2
result2 = chain2.invoke({"dish": "김치볶음밥"})

print(f"요리: {result2.dish_name}")
print(f"난이도: {result2.difficulty} | 시간: {result2.cooking_time}")
print(f"재료:")
for ing in result2.ingredients:
    print(f"  - {ing.name}: {ing.amount}")
print(f"조리 단계:")
for i, step in enumerate(result2.steps, 1):
    print(f"  {i}. {step}")
