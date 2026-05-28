"""
[Task] AI 여행 플래너

도시 하나를 입력하면 음식 / 관광지 / 호텔 추천을 동시에 생성합니다.
서로 독립적인 작업이므로 RunnableParallel 로 묶어 한 번에 호출.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

food_chain  = ChatPromptTemplate.from_template("{city}의 대표 음식 3가지를 한 줄씩 추천해줘.")  | llm | StrOutputParser()
place_chain = ChatPromptTemplate.from_template("{city}의 관광지 3곳을 한 줄씩 추천해줘.")     | llm | StrOutputParser()
hotel_chain = ChatPromptTemplate.from_template("{city}의 추천 호텔 3곳을 한 줄씩 추천해줘.") | llm | StrOutputParser()

travel_chain = RunnableParallel({
    "food":   food_chain,
    "places": place_chain,
    "hotel":  hotel_chain,
})

result = travel_chain.invoke({"city": "도쿄"})

print("🍽️  [대표 음식]")
print(result["food"])
print("\n🗺️  [관광지]")
print(result["places"])
print("\n🏨 [호텔]")
print(result["hotel"])
