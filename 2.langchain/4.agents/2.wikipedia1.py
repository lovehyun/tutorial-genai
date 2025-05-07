from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)

# 위키피디아 도구 로드 (API 키 필요 없음)
tools = load_tools(["wikipedia"])

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 정보 요청
result = agent.invoke({"input": "인공지능의 역사에 대해 간략히 설명해줘"})
print(result["output"])
