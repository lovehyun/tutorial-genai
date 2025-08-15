# pip install wikipedia

from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType

from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

# 0. 환경 변수 로드
load_dotenv()

# 1. OpenAI 모델 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 위키피디아 도구 로드 (API 키 필요 없음)
# tools = load_tools(["wikipedia"])
wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="ko"))
tools = [wiki]

# 3. 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    max_iterations=20,
    verbose=True
)

# 4. 정보 요청
result = agent.invoke({"input": "인공지능의 역사에 대해 간략히 설명해줘"})
print(result["output"])
