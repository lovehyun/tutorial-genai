from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

# MCP 도구 호출 함수들
def call_mcp_say_hello(name: str) -> str:
    async def run_tool():
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("say_hello", {"name": name})
                content = result.content[0].text
                return json.loads(content)["greeting"]
    return asyncio.run(run_tool())

def call_mcp_add(input_str: str) -> str:
    # LangChain이 "10, 25" 형태로 전달하는 입력을 파싱
    try:
        # 따옴표 제거
        input_str = input_str.strip("'\"")
        
        if ',' in input_str:
            parts = input_str.split(',')
            a, b = int(parts[0].strip()), int(parts[1].strip())
        else:
            parts = input_str.split()
            a, b = int(parts[0]), int(parts[1])
        
        async def run_tool():
            server_params = StdioServerParameters(command="python", args=["server2.py"])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("add", {"a": a, "b": b})
                    return result.content[0].text
        
        return asyncio.run(run_tool())
        
    except Exception as e:
        return f"계산 오류: {str(e)}"

def call_mcp_now(*args) -> str:
    async def run_tool():
        server_params = StdioServerParameters(command="python", args=["server2.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("now")
                return result.content[0].text
    return asyncio.run(run_tool())

# LangChain 도구들
tools = [
    Tool(
        name="say_hello",
        func=call_mcp_say_hello,
        description="입력된 이름으로 인사합니다."
    ),
    Tool(
        name="add", 
        func=call_mcp_add,
        description="두 숫자를 더합니다. 입력 형식: '숫자1, 숫자2' 예: '10, 25'"  # 명확한 형식 안내
    ),
    Tool(
        name="now",
        func=call_mcp_now,
        description="현재 시간을 알려줍니다."
    )
]

# LangChain Agent 설정
llm = ChatOpenAI(temperature=0)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True   # 추가
)

# 테스트 실행
if __name__ == "__main__":
    test_cases = [
        "Alice에게 인사해줘",
        "10 더하기 25는 얼마야?", 
        "지금 몇 시야?",
    ]
    
    for test in test_cases:
        print(f"\n[User] 사용자: {test}")
        response = agent.run(test)
        print(f"[ChatBot] 결과: {response}")
        print("-" * 40)
