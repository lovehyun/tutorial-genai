# 필요한 패키지 설치
# pip install -U langchain_openai langchain_experimental langchain_community
# https://serper.dev/

# 필요한 패키지 설치:
# pip install -U langchain_openai langchain_experimental langchain_community

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
from langchain_community.utilities import GoogleSearchAPIWrapper, WikipediaAPIWrapper
from langchain.chains import LLMMathChain
from langchain.tools import Tool
import os

# 0. 환경 변수 로드
load_dotenv()

# 1. Google API 환경 변수 확인
google_cse_id = os.getenv("GOOGLE_CSE_ID")
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_cse_id or not google_api_key:
    raise ValueError("GOOGLE_CSE_ID 또는 GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다.")

# 2. GPT-4o-mini 모델 설정 (모든 곳에 동일하게 사용)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)  # 수학 및 검색 계획용

# 3. 수학 계산 체인
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

# 4. 도구 설정
search = GoogleSearchAPIWrapper()
wikipedia = WikipediaAPIWrapper()

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for answering questions using Google Search."
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

# 5. 계획 및 실행 에이전트 구성
planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)

agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

# 6. 질의 실행
prompt = "Where are the next summer olympics going to be hosted? What is the population of that country divided by 2?"
result = agent.invoke(prompt)

# 7. 결과 출력
print(result)
