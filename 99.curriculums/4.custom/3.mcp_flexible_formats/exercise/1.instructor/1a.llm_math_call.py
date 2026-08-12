"""
llm-math 빌트인 — 자연어 수식을 LLM 이 풀어주는 계산 도구.
load_tools(["llm-math"]) 로 Calculator 도구를 끼운 현행 create_agent.

원본: 2.langchain/8.agents/1.builtin_tools/1.1_llm_math.py
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


# ─── 실행 결과 (2026-08-12, gpt-4o-mini) ──────────────────────
# \( (12.5 \times 4) + 7 \)의 제곱근은 약 7.55입니다.
