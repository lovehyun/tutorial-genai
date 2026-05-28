"""
RunnableParallel — 같은 입력을 여러 체인에 동시 실행하는 Runnable.
이 예제: 도시 정보를 병렬 수집(음식/관광지/호텔)한 뒤 LLM 이 종합 평가하는 map-reduce 패턴.

1단계: 같은 입력을 여러 체인으로 동시에 분석 (map)
2단계: 그 결과들을 다시 LLM에게 넘겨 종합 평가 (reduce)

LCEL 의 dict 리터럴 = RunnableParallel 단축 표기 입니다.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

food_chain  = ChatPromptTemplate.from_template("{city}의 대표 음식 3가지를 한 줄씩.") | llm | StrOutputParser()
place_chain = ChatPromptTemplate.from_template("{city}의 관광지 3곳을 한 줄씩.")     | llm | StrOutputParser()
hotel_chain = ChatPromptTemplate.from_template("{city}의 추천 호텔 3곳을 한 줄씩.") | llm | StrOutputParser()

# 종합 평가용 프롬프트
summarize_prompt = ChatPromptTemplate.from_template(
    "다음 정보를 종합해서 {city} 여행 추천도를 한 단락으로 평가해줘.\n\n"
    "음식: {food}\n관광지: {places}\n호텔: {hotel}"
)

# map: city 유지 + 3개 체인 병렬 수집  →  reduce: 합쳐서 평가
chain = (
    RunnablePassthrough.assign(
        food=food_chain,
        places=place_chain,
        hotel=hotel_chain,
    )
    | summarize_prompt
    | llm
    | StrOutputParser()
)

result = chain.invoke({"city": "도쿄"})
print(result)
