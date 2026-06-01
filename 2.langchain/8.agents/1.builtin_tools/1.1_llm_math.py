"""
llm-math 빌트인 — 자연어 수식을 LLM 이 풀어주는 계산 도구.
이 예제: load_tools(["llm-math"]) 로 Calculator 도구를 끼운 현행 create_agent.

  - 옛 튜토리얼의 initialize_agent + llm-math 예제를 현행 create_agent 로 옮긴 것.
  - llm-math 는 LLM 으로 수식을 파싱하므로 load_tools 에 llm 인자가 필요 (wikipedia/arxiv 와 다름).
  - 내부적으로 numexpr 로 안전 계산.

  ※ pip install numexpr
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# llm-math 는 llm 이 필요한 도구 → load_tools(["llm-math"], llm=llm)
tools = load_tools(["llm-math"], llm=llm)   # 도구 이름: "Calculator"

agent = create_agent(llm, tools)

result = agent.invoke({"messages": [("user", "(12.5 * 4) + 7 의 제곱근을 계산해줘")]})
print(result["messages"][-1].content)

