from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화 
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# Google Search 도구 로드
# 참고: GOOGLE_API_KEY와 GOOGLE_CSE_ID 환경 변수 필요
tools = load_tools(["google-search"])

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 에이전트에게 검색 요청
result = agent.invoke({"input": "서울의 오늘 날씨는 어때?"})
print(result["output"])
