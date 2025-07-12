# 필요한 패키지 설치
# pip install -U langchain_openai langchain_experimental langchain_community
# https://serper.dev/

from dotenv import load_dotenv
from langchain_openai import OpenAI, ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain_community.utilities import GoogleSerperAPIWrapper, WikipediaAPIWrapper
from langchain.chains import LLMMathChain
from langchain.tools import Tool

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
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1) # 단일 텍스트 생성용 모델
chat_model = ChatOpenAI(temperature=0.1) # 대화형 모델 (계획 단계에서 사용)

# 2. 도구 설정 
# LLMMathChain: 수학적 계산을 처리하는 체인
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

# GoogleSerperAPIWrapper: 최신 정보와 현재 이벤트 검색용 (SERPER_API_KEY 환경 변수 필요)
search = GoogleSerperAPIWrapper()

# WikipediaAPIWrapper: 사실과 통계 정보를 위한 위키피디아 접근용
wikipedia = WikipediaAPIWrapper()

# 3. 에이전트가 사용할 도구 목록 정의
tools = [
    Tool(
        name="Search", # 도구 이름
        func=search.run, # 실행할 함수
        description="Useful for answering questions about current events."
    ),
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="Useful for looking up facts and statistics."
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="Useful for answering math-related questions."
    ),
]

# 4. Plan-and-Execute 에이전트 설정
# 계획자(Planner): 전체 작업을 위한 단계별 계획을 생성
planner = load_chat_planner(chat_model) 

# 실행자(Executor): 계획의 각 단계를 실행
executor = load_agent_executor(chat_model, tools, verbose=True)

# PlanAndExecute 에이전트: 계획 생성 후 단계별 실행
# verbose=True: 계획 및 실행 과정의 세부 정보 출력
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

# 5. 복합 질의 실행
# 다음 하계 올림픽 개최지와 해당 국가 인구를 계산하는 질문
prompt = "Where are the next summer olympics going to be hosted? What is the population of that country divided by 2?"
result = agent.invoke(prompt)

# 6. 결과 출력
print(result)
