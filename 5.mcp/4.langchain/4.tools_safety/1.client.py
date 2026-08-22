# 1.client.py - 제한 없는 기본 에이전트 (현행 create_agent)
# 등록된 도구(hello/add/now)는 쓰되, 범위 밖 요청은 LLM 이 임의로 답할 수 있음 → 2.client2_restrict 와 대비.
# (옛 create_react_agent + AgentExecutor + hub → create_agent. 비교: 8.mcp/4.langchain/0.legacy(deprecated)/)
import asyncio
import re
from typing import Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_core.tools import BaseTool           # (구) langchain.tools → 현행 langchain_core.tools
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

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


# Pydantic 스키마 정의
class HelloInput(BaseModel):
    name: str = Field(description="인사할 사람의 이름")


class AddInput(BaseModel):
    input_str: str = Field(description="더할 두 숫자가 포함된 문자열 (예: '3과 5를 더해줘')")


class NowInput(BaseModel):
    query: str = Field(description="시간 조회 요청", default="")


# 커스텀 도구 클래스들 (BaseTool._run = 동기 → create_agent 의 동기 invoke 에서 안전)
class HelloTool(BaseTool):
    name: str = "hello"
    description: str = "이름을 받아 인사하는 도구입니다."
    args_schema: Type[BaseModel] = HelloInput

    def _run(self, name: str) -> str:
        return run_mcp_tool("hello", {"name": name})


class AddTool(BaseTool):
    name: str = "add"
    description: str = "두 정수를 더하는 도구입니다. 예: '3과 5를 더해줘'"
    args_schema: Type[BaseModel] = AddInput

    def _run(self, input_str: str) -> str:
        nums = list(map(int, re.findall(r'\d+', input_str)))
        if len(nums) < 2:
            return "두 개의 숫자를 입력해 주세요."
        return run_mcp_tool("add", {"a": nums[0], "b": nums[1]})


class NowTool(BaseTool):
    name: str = "now"
    description: str = "현재 시간을 반환합니다."
    args_schema: Type[BaseModel] = NowInput

    def _run(self, query: str = "") -> str:
        return run_mcp_tool("now")


tools = [HelloTool(), AddTool(), NowTool()]

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
# 옛 create_react_agent(llm, tools, hub.pull("hwchase17/react")) + AgentExecutor → 아래 한 줄
agent = create_agent(llm, tools)


if __name__ == "__main__":
    questions = [
        "John 에게 인사해줘",
        "3이랑 7을 더해줘",
        "지금 몇 시야?",
        "3과 7을 빼줘",      # 지원하지 않는 연산 (제한이 없어 LLM 이 직접 답할 수 있음)
        "어떤 옷을 입을까?",  # 관련 도구 없음
    ]
    for q in questions:
        print(f"\n질문: {q}")
        try:
            result = agent.invoke({"messages": [("user", q)]})
            print("응답:", result["messages"][-1].content)
        except Exception as e:
            print("오류 발생:", str(e))
