# 필요한 패키지 설치 (최신 업데이트 적용)
# pip install -U langchain_openai

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# 환경 변수 로드
load_dotenv()

# OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 최신 방식으로 툴 로드
tools = load_tools(["human"])
# load_tools(["human"])로 기성(빌트인) Human 툴을 꺼내 씁니다. 
# 빠르고 간단하지만 커스터마이즈가 거의 불가하고 stdin(터미널/노트북) 전제입니다.

# LangChain 에이전트 초기화
agent_chain = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 모델 실행
# result = agent_chain.invoke({"input": "What's my nickname?"})
result = agent_chain.invoke({"input": "내 이름은 뭐야?"})
print(result)
