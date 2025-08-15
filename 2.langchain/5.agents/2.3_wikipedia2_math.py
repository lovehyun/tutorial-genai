# https://python.langchain.com/docs/modules/agents/

# 필요한 패키지 설치 (최신 업데이트 적용)
# pip install langchain_openai wikipedia llm-math numexpr

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.2)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# 2. 툴 로드
tools = load_tools(["wikipedia", "llm-math"], llm=llm)

# 3. LangChain 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. 프롬프트 설정
# prompt = "대한민국의 공휴일 날짜들은? 그리고 이 날짜들의 월과 일의 숫자들의 합산은?"
# prompt = "대한민국의 공휴일 날짜들을 알려주세요. 그리고 각 공휴일의 월과 일을 숫자로 더한 값들의 총합을 계산해주세요. 각 계산 과정도 보여주세요."
prompt = """
1. Find the list of public holidays in South Korea with their specific dates (month and day).
2. For each holiday, add the month number and day number. For example, for January 1st, add 1 + 1 = 2.
3. Then sum all these values to get a final result.
Please list each calculation step clearly.
"""

# 5. 모델 실행
result = agent.invoke({"input": prompt})
print(result)
