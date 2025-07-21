import asyncio
import re
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

load_dotenv()  # 환경 변수 불러오기

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

# 숫자 2개 추출 함수 (add용)
def _extract_two_numbers(text: str) -> dict:
    nums = list(map(int, re.findall(r'\d+', text)))
    if len(nums) < 2:
        raise ValueError("두 개의 숫자를 입력해 주세요.")
    return {"a": nums[0], "b": nums[1]}

# MCP 도구들을 LangChain 도구로 감싸기
mcp_tools = [
    Tool(
        name="hello",
        func=lambda name: run_mcp_tool("hello", {"name": name}),
        description="이름을 받아 인사하는 도구입니다. 입력: 이름 문자열"
    ),
    Tool(
        name="now",
        func=lambda _: run_mcp_tool("now", {"value": "now"}),
        description="현재 시간을 반환합니다. 입력값은 사용되지 않지만 반드시 하나의 문자열 입력이 필요합니다."
    ),
    Tool(
        name="add",
        func=lambda input_str: run_mcp_tool("add", _extract_two_numbers(input_str)),
        description="두 정수를 더하는 도구입니다. 예: '3과 5를 더해줘'"
    )
]

# 커스텀 프롬프트 설정
prefix = """당신은 오직 아래 도구만 사용할 수 있는 AI입니다:

{tools}

아래 도구 목록 외의 도구를 사용하려고 하면 시스템이 종료됩니다.
도구가 없으면 반드시 다음과 같이 대답해야 합니다:
Final Answer: 죄송합니다. 그 작업은 할 수 없습니다.

절대 아래 형식을 벗어나지 마세요:
Action: <tool name>
Action Input: <input>

혹은:
Final Answer: <your answer>
"""

suffix = """질문: {input}
{agent_scratchpad}"""

prompt = PromptTemplate(
    input_variables=["input", "tools", "agent_scratchpad"],
    template=prefix + suffix,
)

# LangChain 에이전트 초기화
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=mcp_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    early_stopping_method="generate",
    prompt=prompt
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
        print(f"\n질문: {q}")
        try:
            result = agent.invoke({"input": q})
            print("응답:", result)
        except Exception as e:
            print("지원하지 않는 요청입니다:", e)
