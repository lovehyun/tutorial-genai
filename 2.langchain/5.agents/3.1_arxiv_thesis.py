# pip install arxiv
from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. arXiv 도구 로드 (API 키 필요 없음)
tools = load_tools(["arxiv"])

# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    max_iterations=20,  # 기본값 15
    verbose=True
)

# 4. 논문 검색 요청
result = agent.invoke({"input": "최근의 딥러닝 관련 논문을 찾아서 요약해줘"})
print(result["output"])
