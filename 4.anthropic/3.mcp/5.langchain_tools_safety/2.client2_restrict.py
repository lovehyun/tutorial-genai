# client_restrict.py - 명령어 제한(Safety 강화 버전)
import asyncio
import re
from typing import Type, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate

load_dotenv()

# MCP 도구 실행 함수
def run_mcp_tool(tool_name: str, tool_input: dict = None) -> str:
    async def _run():
        server_params = StdioServerParameters(command="python", args=["server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, tool_input or {})
                return result.content[0].text
    return asyncio.run(_run())

# 숫자 추출 함수
def _extract_two_numbers(text: str) -> dict:
    nums = list(map(int, re.findall(r'\d+', text)))
    if len(nums) < 2:
        raise ValueError("두 개의 숫자를 입력해 주세요.")
    return {"a": nums[0], "b": nums[1]}

# Pydantic 스키마 정의
class HelloInput(BaseModel):
    name: str = Field(description="인사할 사람의 이름")

class AddInput(BaseModel):
    input_str: str = Field(description="더할 두 숫자가 포함된 문자열")

class NowInput(BaseModel):
    query: str = Field(description="시간 조회 요청", default="")

# 커스텀 도구 클래스들
class HelloTool(BaseTool):
    name: str = "hello"
    description: str = "이름을 받아 인사하는 도구입니다. 입력: 이름 문자열"
    args_schema: Type[BaseModel] = HelloInput

    def _run(self, name: str) -> str:
        return run_mcp_tool("hello", {"name": name})

class NowTool(BaseTool):
    name: str = "now"
    description: str = "현재 시간을 반환합니다. 입력값은 사용되지 않지만 반드시 하나의 문자열 입력이 필요합니다."
    args_schema: Type[BaseModel] = NowInput

    def _run(self, query: str = "") -> str:
        return run_mcp_tool("now", {"value": "now"})

class AddTool(BaseTool):
    name: str = "add"
    description: str = "두 정수를 더하는 도구입니다. 예: '3과 5를 더해줘'"
    args_schema: Type[BaseModel] = AddInput

    def _run(self, input_str: str) -> str:
        try:
            params = _extract_two_numbers(input_str)
            return run_mcp_tool("add", params)
        except ValueError as e:
            return str(e)

# 도구 리스트
tools = [HelloTool(), NowTool(), AddTool()]

# 커스텀 프롬프트 템플릿 (최신 ReAct 형식)
template = """당신은 오직 아래 도구만 사용할 수 있는 AI입니다:

{tools}

Tool names: {tool_names}

아래 도구 목록 외의 도구를 사용하려고 하면 시스템이 종료됩니다.
도구가 없으면 반드시 다음과 같이 대답해야 합니다:
Final Answer: 죄송합니다. 그 작업은 할 수 없습니다.

사용 가능한 도구로 답변할 수 있는 경우에만 도구를 사용하세요.

다음 형식을 정확히 따르세요:

Question: 답변해야 할 질문
Thought: 무엇을 해야 하는지 생각해보세요
Action: 사용할 도구 이름 [{tool_names}에서 선택]
Action Input: 도구에 전달할 입력
Observation: 도구 실행 결과
... (이 Thought/Action/Action Input/Observation 과정을 반복할 수 있음)
Thought: 이제 최종 답변을 알았습니다
Final Answer: 사용자에게 줄 최종 답변

시작하세요!

Question: {input}
Thought: {agent_scratchpad}"""

prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad"],
    partial_variables={
        "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
        "tool_names": ", ".join([tool.name for tool in tools])
    },
    template=template
)

# LangChain 에이전트 초기화 (최신 방식)
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# 에이전트 생성
agent = create_react_agent(llm, tools, prompt)

# 에이전트 실행기
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3,
    early_stopping_method="generate"
)

# 테스트 실행
if __name__ == "__main__":
    questions = [
        "John 에게 인사해줘",
        "3이랑 7을 더해줘",
        "지금 몇 시야?",
        "3과 7을 빼줘",
        "어떤 옷을 입을까?",
        "오늘 날씨는?"
    ]

    for q in questions:
        print(f"\n{'='*50}")
        print(f"질문: {q}")
        print('='*50)
        try:
            result = agent_executor.invoke({"input": q})
            print(f"응답: {result['output']}")
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            
    print(f"\n{'='*50}")
    print("테스트 완료!")
    print('='*50)


# 기능                    첫 번째 버전                두 번째 버전 (Safety)
# 지원하지 않는 요청       에러 발생하거나 임의 응답    명확한 거부 메시지
# 도구 범위               제한 없음                   엄격하게 3개 도구만
# 응답 일관성             불일치 가능                 일관된 거부 메시지
# 예측 가능성             예측 어려움                 예측 가능한 행동

# 실제 동작 차이
# 질문: "3과 7을 빼줘"
# 첫 번째 버전:
#  - 뺄셈 도구가 없어서 에러 발생하거나
#  - LLM이 직접 계산을 시도할 수 있음
#  - 일관성 없는 응답
# 두 번째 버전 (Safety):
#  - 명확한 응답: "죄송합니다. 그 작업은 할 수 없습니다."
#  - 항상 일관된 거부 메시지
#  - 사용자에게 명확한 한계 전달
#
# Safety의 중요성
# 1. 예측 가능성: 사용자가 시스템의 한계를 명확히 알 수 있음
# 2. 일관성: 같은 유형의 요청에 대해 항상 같은 방식으로 응답
# 3. 투명성: "할 수 없다"고 솔직하게 말함
# 4. 안전성: 범위를 벗어난 작업을 시도하지 않음
#
# 따라서 두 번째 파일은 엔터프라이즈나 프로덕션 환경에서 AI 에이전트의 행동을 엄격하게 제어하고 싶을 때 사용하는 Safety 강화 패턴입니다.
