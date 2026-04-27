# 필요한 패키지 설치
# pip install -U langchain_openai langchain_experimental langchain_community
# https://serper.dev/

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.chains import LLMMathChain

# 환경 변수 로드
load_dotenv()

import os

# 환경 변수 확인
serper_api_key = os.getenv("SERPER_API_KEY")

if serper_api_key:
    print("SERPER_API_KEY 환경 변수가 설정되어 있습니다.")
    # 마스킹된 형태로 출력 (보안을 위해)
    masked_key = serper_api_key[:4] + '*' * (len(serper_api_key) - 8) + serper_api_key[-4:]
    print(f"API 키: {masked_key}")
else:
    print("SERPER_API_KEY 환경 변수가 설정되어 있지 않습니다.")
    print("이 키가 없으면 GoogleSerperAPIWrapper가 작동하지 않습니다.")
    
    
# 1. OpenAI 모델 초기화
# temperature: 값이 낮을수록 더 일관된(결정적인) 출력을 생성
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1) # 단일 텍스트 생성용 모델
planner_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
executor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 도구 설정

# GoogleSerperAPIWrapper: 최신 정보와 현재 이벤트 검색용 (SERPER_API_KEY 환경 변수 필요)
# search = GoogleSerperAPIWrapper()
# search = GoogleSerperAPIWrapper(hl="en", gl="us", k=5)
search = GoogleSerperAPIWrapper(hl="ko", gl="kr", k=5) # hl=한국어 UI 선호, gl=한국 지역 힌트, 상위 5개

# WikipediaAPIWrapper: 사실과 통계 정보를 위한 위키피디아 접근용
# wiki = WikipediaAPIWrapper()
wiki = WikipediaAPIWrapper(lang="ko")  # ko/auto 등 사용 가능

# 수학적 계산
math_chain = LLMMathChain.from_llm(llm=executor_llm, verbose=False)

# 3. 에이전트가 사용할 도구 목록 정의
tools = [
    Tool(
        name="Search", # 도구 이름
        func=search.run, # 실행할 함수
        description="Useful for answering questions about current events."
    ),
    Tool(
        name="Wikipedia",
        func=wiki.run,
        description="Useful for looking up facts and statistics."
    ),
    Tool(
        name="Calculator",
        func=math_chain.run,
        description="Useful for answering math-related questions."
    ),
]

# 4. Plan-and-Execute 에이전트 설정
planner_prompt = PromptTemplate.from_template(
"""Break down the following question into clear sequential steps, 
specifying which tool to use for each step.

Question: {input}
Plan:"""
)

planner_chain = planner_prompt | planner_llm | StrOutputParser()

# 5. Executor Agent: 계획 단계별 실행
executor_agent = initialize_agent(
    tools,  # Search/Wikipedia/Calculator
    executor_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# 6. 실행 로직
# 다음 하계 올림픽 개최지와 해당 국가 인구를 계산하는 질문
question  = (
    "Where are the next summer olympics going to be hosted? "
    "What is the population of that country divided by 2?"
)

plan = planner_chain.invoke({"input": question})
print("\n[PLAN]\n", plan)

final_answer = executor_agent.invoke({"input": question})
print("\n[FINAL ANSWER]\n", final_answer["output"])
