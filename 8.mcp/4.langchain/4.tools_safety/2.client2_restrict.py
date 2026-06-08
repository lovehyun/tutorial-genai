# 2.client2_restrict.py - 명령어 제한 (Safety 강화 버전, 현행 create_agent)
# 안전장치 = system_prompt 로 "등록 도구로 못 하는 요청은 고정 거부 메시지" 강제.
# 1.client.py(무제한) 와 대비: 범위 밖 요청에 일관된 거부 응답.
# (옛 create_react_agent + AgentExecutor + 수동 ReAct 프롬프트 → create_agent + system_prompt. 비교: 0.legacy(deprecated)/)
import asyncio
import re
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()


def run_mcp_tool(tool_name: str, tool_input: dict = None) -> str:
    async def _run():
        server_params = StdioServerParameters(command="python", args=["server.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, tool_input or {})
                return result.content[0].text
    return asyncio.run(_run())


def _extract_two_numbers(text: str) -> dict:
    nums = list(map(int, re.findall(r'\d+', text)))
    if len(nums) < 2:
        raise ValueError("두 개의 숫자를 입력해 주세요.")
    return {"a": nums[0], "b": nums[1]}


class HelloInput(BaseModel):
    name: str = Field(description="인사할 사람의 이름")


class AddInput(BaseModel):
    input_str: str = Field(description="더할 두 숫자가 포함된 문자열")


class NowInput(BaseModel):
    query: str = Field(description="시간 조회 요청", default="")


class HelloTool(BaseTool):
    name: str = "hello"
    description: str = "이름을 받아 인사하는 도구입니다. 입력: 이름 문자열"
    args_schema: Type[BaseModel] = HelloInput

    def _run(self, name: str) -> str:
        return run_mcp_tool("hello", {"name": name})


class NowTool(BaseTool):
    name: str = "now"
    description: str = "현재 시간을 반환합니다."
    args_schema: Type[BaseModel] = NowInput

    def _run(self, query: str = "") -> str:
        return run_mcp_tool("now")


class AddTool(BaseTool):
    name: str = "add"
    description: str = "두 정수를 더하는 도구입니다. 예: '3과 5를 더해줘'"
    args_schema: Type[BaseModel] = AddInput

    def _run(self, input_str: str) -> str:
        try:
            return run_mcp_tool("add", _extract_two_numbers(input_str))
        except ValueError as e:
            return str(e)


tools = [HelloTool(), NowTool(), AddTool()]

# ─── 안전장치: 화이트리스트 + 고정 거부 (system_prompt 로 강제) ───
SAFETY_PROMPT = (
    "당신은 오직 다음 도구만 사용할 수 있습니다: hello(인사), add(두 정수 덧셈), now(현재 시간).\n"
    "이 도구들로 처리할 수 없는 요청(예: 뺄셈/곱셈, 날씨, 추천 등)에는 도구를 쓰지 말고, "
    "정확히 이렇게만 답하세요: '죄송합니다. 그 작업은 할 수 없습니다.'\n"
    "직접 계산하거나 추측하지 마세요."
)

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
agent = create_agent(llm, tools, system_prompt=SAFETY_PROMPT)


if __name__ == "__main__":
    questions = [
        "John 에게 인사해줘",
        "3이랑 7을 더해줘",
        "지금 몇 시야?",
        "3과 7을 빼줘",        # 미지원 → 고정 거부
        "어떤 옷을 입을까?",    # 도구 없음 → 고정 거부
        "오늘 날씨는?",        # 도구 없음 → 고정 거부
    ]
    for q in questions:
        print(f"\n{'='*50}\n질문: {q}\n{'='*50}")
        try:
            result = agent.invoke({"messages": [("user", q)]})
            print(f"응답: {result['messages'][-1].content}")
        except Exception as e:
            print(f"오류 발생: {e}")

# 정리:
#   - 무제한(1.client) vs 화이트리스트+고정거부(2): 같은 도구셋이라도 system_prompt 로 행동을 통제.
#   - create_agent 는 등록된 도구만 호출 가능 → 범위 밖은 프롬프트로 일관 거부.
#   - 더 강한 가드레일은 미들웨어(PIIMiddleware 등, 2.langchain/8.agents/12.middleware) 참고.
