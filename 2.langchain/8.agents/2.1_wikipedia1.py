# pip install wikipedia

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 엔드포인트 / 패러다임
# OpenAI: (예전) 텍스트 컴플리션 스타일. gpt-3.5-turbo-instruct 같은 인스트럭트 계열에 맞춤 → 현재 대부분 중단.
# ChatOpenAI: 채팅/메시지 기반 모델(4o/4.1/4-mini 등). 도구 호출(Function/Tool Calling)과 에이전트에 최적화.

# 2. 위키피디아 도구 로드 (API 키 필요 없음)
tools = load_tools(["wikipedia"])
# llm-math는 llm 을 필요로 하는 반면 "wikipedia" 같은 툴은 LLM 없이도 동작하므로 llm 인자가 필요 없습니다.


# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 4. 정보 요청
result = agent.invoke({"input": "인공지능의 역사에 대해 간략히 설명해줘"})
print(result["output"])
