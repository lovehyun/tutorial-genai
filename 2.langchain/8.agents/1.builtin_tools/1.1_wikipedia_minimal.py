"""
가장 단순한 에이전트 — 도구를 "만들지" 않고 "가져다" 쓴다.
이 예제: load_tools 로 빌트인 위키피디아 도구를 끼우고, create_agent 한 줄로 끝낸다.

여기서 배우는 건 딱 하나: "에이전트 = LLM + 도구 리스트" 라는 골격.
  - @tool 함수 정의 X     → 그건 2.custom_tools 에서
  - system_prompt·메시지 순회·안전장치 X → 그건 1.2_wikipedia.py 부터 빌드업

  ※ pip install wikipedia

흐름:
  1) load_tools(["wikipedia"]) → 미리 포장된 도구 1개를 리스트로 받음
  2) create_agent(llm, tools)  → 에이전트 완성 (ReAct 루프는 내부에서 자동)
  3) invoke → 최종 답변만 꺼내 출력
"""

import wikipedia
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import create_agent

load_dotenv()

# Wikipedia 는 2024+ 부터 기본 User-Agent 를 차단 → 일반 브라우저 UA 로 교체해야 동작
# (안 하면 빈 응답이 와서 JSONDecodeError. Wikimedia User-Agent 정책)
wikipedia.wikipedia.USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


# 1) 빌트인 도구를 "이름" 으로 불러온다 — 직접 만들 필요 없음
tools = load_tools(["wikipedia"])

# 2) LLM + 도구 = 에이전트 (한 줄)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, tools)

# 3) 실행 — 최종 답변만
result = agent.invoke({"messages": [("user", "파이썬 프로그래밍 언어는 누가 만들었어?")]})
print(result["messages"][-1].content)
