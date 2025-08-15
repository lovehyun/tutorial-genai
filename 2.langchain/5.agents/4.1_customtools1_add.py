from dotenv import load_dotenv

from langchain_openai import OpenAI, ChatOpenAI
from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
import re

import warnings
from langchain_core._api.deprecation import LangChainDeprecationWarning
warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)


# .env 파일에서 환경 변수 로드
load_dotenv()

# LLM 초기화
# llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 간단한 도구 만들기
# @tool 데코레이터의 역할은 함수를 LangChain 에이전트가 사용할 수 있는 도구로 변환하는 것입니다. 에이전트는 이 도구의 기능과 사용 방법을 다음과 같은 방식으로 파악합니다:
#  - 함수 이름: 에이전트는 함수 이름(예: add, multiply)을 보고 도구의 기본 기능을 파악합니다.
#  - Docstring(문서 문자열): 함수 아래에 작성된 """두 숫자 a와 b를 곱합니다."""와 같은 문서 문자열은 도구의 설명으로 사용됩니다. 에이전트는 이 설명을 읽고 도구가 무엇을 하는지 이해합니다.
#  - 파라미터 타입 힌트: 함수 정의에 있는 a: int, b: int와 같은 타입 힌트는 에이전트에게 어떤 타입의 입력이 필요한지 알려줍니다.
#  - 반환 타입 힌트: -> int와 같은 반환 타입 힌트는 에이전트에게 어떤 결과가 반환될지 알려줍니다.

################################################################
# 단순 도구만 정의
################################################################
# 단일 입력 도구 만들기 - 문자열로 입력 받기

@tool
def add(query: str) -> int:
    """두 숫자를 더합니다. 형식: '숫자1 숫자2'"""
    a, b = map(int, query.split())
    return a + b

################################################################
# 예외 처리 (입력값 필터링, 인자 개수 처리)
################################################################
@tool
def add_better(query: str) -> int:
    """두 숫자를 더합니다. 형식: '숫자1 숫자2'"""
    query = query.replace("'", "").replace('"', "").strip()
    nums = list(map(int, re.findall(r"-?\d+", query))) # 양수/음수 한자리 또는 그 이상의 숫자
    if len(nums) < 2:
        raise ValueError("두 개의 숫자가 필요합니다.")
    return nums[0] + nums[1]

################################################################
# 예외 처리 및 핸들링 (오류 메시지 반환을 통한 LLM 추가 대응)
################################################################
@tool
def add_best(query: str) -> int:
    """두 숫자를 더합니다. 형식: '숫자1 숫자2'"""
    try:
        query = query.replace("'", "").replace('"', "").replace("–", "-").strip()
        nums = list(map(int, re.findall(r"-?\d+", query))) # 양수/음수 한자리 또는 그 이상의 숫자
        if len(nums) < 2:
            return "오류: 두 개의 숫자가 필요합니다."
        return str(nums[0] + nums[1])
    except Exception as e:
        return f"오류 발생: {str(e)}"

################################################################
# 예외 처리 및 핸들링 (오류 메시지 반환을 통한 LLM 추가 대응) 플러스 여러개의 숫자 더함
################################################################
@tool
def add_best_all(query: str) -> str:
    """문자열에 등장하는 모든 정수를 추출하여 합산합니다. 예: '3과 4와 -5' → 2"""
    try:
        q = query.replace("'", "").replace('"', "").replace("–", "-").strip()
        nums = list(map(int, re.findall(r"-?\d+", q)))
        if len(nums) < 1:
            return "오류: 합산할 숫자가 없습니다."
        return str(sum(nums))
    except Exception as e:
        return f"오류 발생: {e}"

# 도구 목록 생성
# tools = [add_better]
tools = [add_better, add_best_all]

# 에이전트 초기화
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 에이전트 실행
# result = agent.invoke({"input": "3과 4를 더해줘."})
# result = agent.invoke({"input": "3과 4와 5를 더해줘."})
result = agent.invoke({"input": "10, -3, 7을 모두 더해줘."})

# result = agent.invoke({"input": "3과 4를 곱해줘"})
# result = agent.invoke({"input": "3과 4를 곱하고, 그 결과에 10을 더해줘."})

print("\n계산:", result)
# print("\n최종 결과:", result["output"])
