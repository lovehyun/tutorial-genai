# LangChain Agent — 수학 계산 도구
# create_react_agent (최신 패턴)

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent as create_react_agent

# 0. 환경 변수 로드
load_dotenv()

# 1. LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. llm-math 도구 로드
tools = load_tools(["llm-math"], llm=llm)

# 3. ReAct 에이전트 생성 (langgraph)
agent = create_react_agent(llm, tools)

# 4. 수학 문제 입력
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the result of (53 * 7 + 2) / 5?"}]}
)

# 마지막 메시지 출력
print(result["messages"][-1].content)
