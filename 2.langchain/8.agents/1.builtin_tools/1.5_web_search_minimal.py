"""
웹 검색 빌트인 — 최소 형태. 실시간 정보 검색 도구를 1개 끼우고 끝.
이 예제: Tavily 검색 도구 하나로 "지금 이 순간" 정보에 답하는 에이전트.

  - load_tools 로딩이 아니라 도구 객체를 직접 1개 만든다 (Tavily 는 별도 패키지)
  - max_results 외 설정·프롬프트·안전장치 없음 (robust 버전은 1.6_web_search.py)
  - Serper / Google CSE 대안 비교도 1.6 에 정리돼 있음

  ※ pip install langchain-tavily   (.env 에 TAVILY_API_KEY 필요)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent

load_dotenv()


# 검색 도구 1개 — 기본 설정
web_search = TavilySearch(max_results=3)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, [web_search])

result = agent.invoke({"messages": [("user", "LangChain 의 최신 버전이 뭐야?")]})
print(result["messages"][-1].content)
