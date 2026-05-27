# pip install langgraph langchain_openai python-dotenv
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

import re


load_dotenv()

# 도구 정의 (덧셈/곱셈 모두 제공)
@tool
def add_two(query: str) -> str:
    """문자열에서 앞의 두 정수를 더해 반환"""
    nums = list(map(int, re.findall(r"-?\d+", query)))
    if len(nums) < 2:
        return "오류: 두 숫자 필요"
    return str(nums[0] + nums[1])

@tool
def multiply_two(query: str) -> str:
    """문자열에서 앞의 두 정수를 곱해 반환"""
    nums = list(map(int, re.findall(r"-?\d+", query)))
    if len(nums) < 2:
        return "오류: 두 숫자 필요"
    return str(nums[0] * nums[1])

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# LangGraph의 프리빌트 ReAct 에이전트 생성
agent = create_react_agent(
    llm,
    tools=[add_two, multiply_two],
    # 도구 사용 규칙을 강제하고 싶다면:
    state_modifier=(
        "모든 산술은 반드시 제공된 도구로 수행하세요. "
        "곱셈은 multiply_two, 덧셈은 add_two만 사용하고 직접 계산하지 마세요. "
        "한국어로 답변하세요."
    ),
)

# 대화 실행
result = agent.invoke({"messages": [("human", "3과 4를 곱하고, 그 결과에 10을 더해줘.")]})
print(result["messages"][-1].content)
