"""
arXiv 빌트인 — 최소 형태. 논문 검색 도구를 load_tools 로 끼우고 끝.
이 예제: 도구를 "만들지" 않고 이름으로 불러와 학술 검색 에이전트를 만든다.

  - 1.1_wikipedia_minimal.py 와 똑같은 골격, 도구만 wikipedia → arxiv 로 교체
  - system_prompt·안전장치 없음 (그 robust 버전은 1.7_arxiv.py 에서 빌드업)

  ※ pip install arxiv
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()


# 빌트인 arxiv 도구를 "이름" 으로 불러온다
tools = load_tools(["arxiv"])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools)

# 검색은 영어 키워드가 정확도 ↑
result = agent.invoke({"messages": [("user", "retrieval-augmented generation 관련 논문 하나 찾아서 한국어로 요약해줘")]})
print(result["messages"][-1].content)

# 다음: 1.7_arxiv.py (arxiv 본격 활용)
