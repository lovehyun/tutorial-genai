"""
[Task] AI 여행 플래너

도시 하나를 입력하면 음식 / 관광지 / 호텔 추천을 동시에 생성합니다.

사용자 입력
    │
    ▼
RunnableBranch
 ├── 여행 추천 요청?
 │      └── RunnableParallel
 │            ├── 음식
 │            ├── 관광지
 │            └── 호텔
 │
 └── 일정/동선 요청?
        └── RunnableParallel
              ├── 시간표
              ├── 동선
              └── 교통수단
"""

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import (
    RunnableParallel,
    RunnableBranch
)

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

# -----------------------------
# 음식 / 관광 / 호텔
# -----------------------------
food_chain = (
    ChatPromptTemplate.from_template(
        "{city}의 대표 음식 3가지를 추천해줘."
    )
    | llm
    | StrOutputParser()
)

place_chain = (
    ChatPromptTemplate.from_template(
        "{city}의 관광지 3곳을 추천해줘."
    )
    | llm
    | StrOutputParser()
)

hotel_chain = (
    ChatPromptTemplate.from_template(
        "{city}의 추천 호텔 3곳을 추천해줘."
    )
    | llm
    | StrOutputParser()
)

travel_recommend_chain = RunnableParallel({
    "food": food_chain,
    "places": place_chain,
    "hotel": hotel_chain,
})

# -----------------------------
# 일정 / 동선 / 교통
# -----------------------------
schedule_chain = (
    ChatPromptTemplate.from_template(
        "{city} 여행 1일 추천 시간표를 작성해줘."
    )
    | llm
    | StrOutputParser()
)

route_chain = (
    ChatPromptTemplate.from_template(
        "{city} 여행 최적 동선을 추천해줘."
    )
    | llm
    | StrOutputParser()
)

transport_chain = (
    ChatPromptTemplate.from_template(
        "{city}에서 효율적인 교통수단을 추천해줘."
    )
    | llm
    | StrOutputParser()
)

planner_chain = RunnableParallel({
    "schedule": schedule_chain,
    "route": route_chain,
    "transport": transport_chain,
})

# -----------------------------
# Branch
# -----------------------------
main_chain = RunnableBranch(

    # 일정/동선 관련 요청
    (
        lambda x: "일정" in x["question"]
               or "동선" in x["question"]
               or "교통" in x["question"],

        planner_chain
    ),

    # 기본값
    travel_recommend_chain
)

# -----------------------------
# 실행
# -----------------------------
result = main_chain.invoke({
    "city": "도쿄",
    # "question": "맛집 추천해줘",
    "question": "동선과 교통수단 추천해줘",
})

print(result)
