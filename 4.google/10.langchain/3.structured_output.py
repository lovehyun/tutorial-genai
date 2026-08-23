# pip install langchain-google-genai langchain-core python-dotenv

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)


# Pydantic 모델로 구조화된 출력 정의
class TechTrend(BaseModel):
    name: str = Field(description="기술 트렌드 이름")
    description: str = Field(description="간단한 설명")
    impact: str = Field(description="산업에 미치는 영향")
    maturity: str = Field(description="성숙도: 초기/성장/성숙")


class TechTrends(BaseModel):
    trends: list[TechTrend] = Field(description="기술 트렌드 목록")


# with_structured_output으로 Pydantic 모델 바인딩
structured_llm = llm.with_structured_output(TechTrends)

result = structured_llm.invoke("2025년 가장 주목할 AI 기술 트렌드 3가지를 알려주세요.")

for trend in result.trends:
    print(f"[{trend.maturity}] {trend.name}")
    print(f"  설명: {trend.description}")
    print(f"  영향: {trend.impact}\n")
