from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
import re

# 0. 환경변수 로드
load_dotenv()

# 1. 최신/안정 모델 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 툴 정의

# 숫자 추출 유틸(음수/다양한 구분자 허용)
def extract_ints(text: str):
    q = text.replace("'", "").replace('"', "").replace("–", "-").strip()
    return list(map(int, re.findall(r"-?\d+", q)))

@tool
def add_two(query: str) -> str:
    """문자열에서 '앞의 두 정수'를 더해 결과를 문자열로 반환합니다."""
    nums = extract_ints(query)
    if len(nums) < 2:
        return "오류: 두 개의 숫자가 필요합니다."
    return str(nums[0] + nums[1])

@tool
def multiply_two(query: str) -> str:
    """문자열에서 '앞의 두 정수'를 곱해 결과를 문자열로 반환합니다."""
    nums = extract_ints(query)
    if len(nums) < 2:
        return "오류: 두 개의 숫자가 필요합니다."
    return str(nums[0] * nums[1])

@tool
def add_all(query: str) -> str:
    """문자열에 등장하는 '모든 정수'를 합산해 문자열로 반환합니다."""
    nums = extract_ints(query)
    if not nums:
        return "오류: 합산할 숫자가 없습니다."
    return str(sum(nums))

tools = [add_two, multiply_two, add_all]

# 3. 에이전트 생성

# StructuredChat으로 도구 사용을 강하게 유도
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={
        "system_message": (
            "모든 산술은 반드시 제공된 도구로 수행하세요. 직접 암산 금지. "
            "덧셈은 add_two 또는 add_all, 곱셈은 multiply_two를 사용하세요. "
            "질문이 한국어라도 도구 입력은 '숫자 숫자' 형태로 간단히 전달하세요. "
            "응답은 한국어로 간결하게 하세요."
        )
    },
    handle_parsing_errors=True,
    max_iterations=6,
    verbose=True,
)

# 4. 예시 실행
result = agent.invoke({"input": "3과 4를 곱하고, 그 결과에 10을 더해줘."})
# print("\n결과:", result)
print("\n최종 결과:", result["output"])
