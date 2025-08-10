# client3_multi_tools.py - 다중 도구 확장 방식 (핵심만)
"""
다중 도구 확장 방식 - 실무에서 가장 권장

장점:
- 여러 도구를 쉽게 추가 가능
- 확장성 뛰어남 (새 도구 추가 시 함수만 추가)
- 도구별 독립적 구현
- 실무 환경에 최적
"""

import asyncio
import os
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_core.tools import Tool

load_dotenv()
os.environ["LANGCHAIN_TRACING_V2"] = "false"


def create_server_compatible_tools():
    """
    server.py와 호환되는 여러 도구들을 생성
    
    핵심 패턴:
    1. 각 도구마다 독립적인 함수 생성
    2. 함수 내부에서 MCP 서버 연결/호출/정리
    3. LangChain Tool 객체로 래핑
    4. 리스트로 반환하여 Agent에 등록
    """
    
    def say_hello_tool(name: str) -> str:
        """인사말 생성 도구 - server.py의 say_hello 호출"""
        async def run():
            server_params = StdioServerParameters(command="python", args=["server.py"])
            
            # 자동 연결 관리: with 블록 종료시 자동 정리
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("say_hello", {"name": name})
                    return result.content[0].text
        
        return asyncio.run(run())
    
    def add_numbers_tool(numbers_text: str) -> str:
        """
        덧셈 도구 (예시) - server.py에 add_numbers 도구 추가시 사용 가능
        
        server.py에 추가할 코드:
        @mcp.tool()
        def add_numbers(a: int, b: int) -> dict:
            return {"result": a + b}
        """
        async def run():
            # 텍스트에서 숫자 추출
            import re
            numbers = re.findall(r'\d+', numbers_text)
            a, b = int(numbers[0]), int(numbers[1])
            
            server_params = StdioServerParameters(command="python", args=["server.py"])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("add_numbers", {"a": a, "b": b})
                    return result.content[0].text
        
        return asyncio.run(run())
    
    def get_time_tool(query: str) -> str:
        """
        시간 조회 도구 (예시) - server.py에 get_time 도구 추가시 사용 가능
        
        server.py에 추가할 코드:
        @mcp.tool()
        def get_time() -> dict:
            from datetime import datetime
            return {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        async def run():
            server_params = StdioServerParameters(command="python", args=["server.py"])
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("get_time")
                    return result.content[0].text
        
        return asyncio.run(run())
    
    # 현재 사용 가능한 도구들 (server.py에 실제로 있는 도구만)
    tools = [
        Tool(
            name="say_hello",
            func=say_hello_tool,
            description="사람 이름을 입력받아 인사말을 생성합니다"
        )
    ]
    
    # 확장 예시 도구들 (server.py에 해당 도구 추가시 주석 해제)
    # tools.extend([
    #     Tool(
    #         name="add_numbers", 
    #         func=add_numbers_tool,
    #         description="두 숫자를 더합니다. 예: '10과 20을 더해주세요'"
    #     ),
    #     Tool(
    #         name="get_time",
    #         func=get_time_tool, 
    #         description="현재 시간을 알려줍니다"
    #     )
    # ])
    
    print(f"등록된 도구 수: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    return tools


async def main():
    """
    메인 실행 함수
    
    실행 흐름:
    1. 여러 도구 생성 및 등록
    2. LLM 및 Agent 설정  
    3. 테스트 쿼리 실행
    4. 결과 확인
    """
    print("다중 도구 확장 방식 MCP 클라이언트")
    print("=" * 50)
    
    # 1. 도구들 생성
    tools = create_server_compatible_tools()
    
    # 2. LangChain Agent 설정
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    prompt = hub.pull("hwchase17/react")  # ReAct 프롬프트 템플릿
    
    # 3. Agent 생성 (여러 도구 등록)
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # 4. 테스트 실행
    test_queries = [
        "Alice에게 인사해줘",
        "Bob에게 Hello라고 말해줘", 
        "Charlie에게 안녕하세요라고 인사해주세요"
        # "10과 20을 더해줘",  # add_numbers 도구 추가시 사용 가능
        # "지금 몇 시야?"        # get_time 도구 추가시 사용 가능
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[테스트 {i}] {query}")
        print("-" * 30)
        response = await agent_executor.ainvoke({"input": query})
        print(f"결과: {response['output']}")
        print("=" * 50)
    
    print("\n확장 방법:")
    print("1. server.py에 새 도구 추가")
    print("2. 이 파일에서 해당 도구 함수 추가")
    print("3. tools 리스트에 Tool 객체 추가")
    print("4. 즉시 사용 가능!")


if __name__ == "__main__":
    asyncio.run(main())
