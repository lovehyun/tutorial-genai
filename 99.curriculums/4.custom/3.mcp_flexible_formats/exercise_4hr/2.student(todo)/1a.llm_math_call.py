"""
llm-math 빌트인 — 자연어 수식을 LLM 이 풀어주는 계산 도구.
load_tools(["llm-math"]) 로 Calculator 도구를 끼운 현행 create_agent.

TODO 3개를 채우면 끝. 채우고 실행해서 계산 결과가 출력되는지 확인하자.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# TODO 1: 빌트인 도구 "llm-math" 를 불러온다.
#   힌트 — load_tools(["llm-math"], llm=llm)
#   llm-math 는 LLM 으로 수식을 파싱하는 도구라 다른 빌트인과 달리 llm 인자가 꼭 필요하다.
tools = None  # ← 여기를 채우세요

# TODO 2: llm 과 tools 로 에이전트를 만든다.
#   힌트 — create_agent(llm, tools)
agent = None  # ← 여기를 채우세요

# TODO 3: 에이전트에게 계산을 시킨다.
#   힌트 — agent.invoke({"messages": [("user", "질문")]})
#   질문 예시: "(12.5 * 4) + 7 의 제곱근을 계산해줘"
result = None  # ← 여기를 채우세요

print(result["messages"][-1].content)
