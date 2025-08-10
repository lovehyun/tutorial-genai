# client3_multi_tools.py - 다중 도구 확장 방식
"""
방법 3: 다중 도구 확장 방식

장점:
- 여러 도구를 쉽게 추가할 수 있음
- 확장성이 뛰어남 (새 도구 추가 시 함수만 추가)
- 방법 2의 안정성을 유지하면서 기능 확장
- 실무 환경에 가장 적합
- 도구별 독립적인 에러 처리

단점:
- 여전히 매번 새 연결 생성 (약간의 오버헤드)
- 도구가 많아지면 코드가 길어짐

결론: 실무에서 가장 권장하는 방식
"""

import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_core.tools import Tool

load_dotenv()

def create_server_compatible_tools():
    """
    server.py와 호환되는 여러 도구들을 생성
    
    특징:
    - 함수 기반으로 간단함
    - 도구별 독립적인 구현
    - 쉬운 확장성 (새 도구 추가 시 함수만 추가)
    - 각 도구마다 자동 연결 관리
    
    현재 server.py에 있는 도구:
    - say_hello: 인사말 생성
    
    확장 가능한 도구들 (server.py에 추가하면 사용 가능):
    - add_numbers: 덧셈 계산
    - get_time: 현재 시간 조회
    - 기타 비즈니스 로직 도구들
    """
    
    def say_hello_tool(name: str) -> str:
        """
        인사말 생성 도구 - server.py의 say_hello와 호환
        
        동작:
        1. MCP 서버 연결
        2. say_hello 도구 호출
        3. 결과 반환
        4. 자동 연결 정리
        """
        async def run():
            server_params = StdioServerParameters(
                command="python", 
                args=["server.py"]
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # server.py의 say_hello 도구 호출
                    result = await session.call_tool("say_hello", {"name": name})
                    return result.content[0].text
        
        try:
            return asyncio.run(run())
        except Exception as e:
            return f"인사말 생성 오류: {str(e)}"
    
    # 확장 예시: server.py에 추가하면 사용할 수 있는 도구들
    def example_add_tool(numbers_text: str) -> str:
        """
        덧셈 도구 (예시) - server.py에 add_numbers 도구가 있다면 사용 가능
        
        주의: 현재 server.py에는 이 도구가 없으므로 에러가 발생합니다.
        server.py에 다음 도구를 추가하면 사용 가능:
        
        @mcp.tool()
        def add_numbers(a: int, b: int) -> dict:
            return {"result": a + b}
        """
        async def run():
            try:
                # 간단한 숫자 추출
                import re
                numbers = re.findall(r'\d+', numbers_text)
                if len(numbers) < 2:
                    return "두 개의 숫자를 찾을 수 없습니다. 예: '10과 20을 더해주세요'"
                
                a, b = int(numbers[0]), int(numbers[1])
                
                server_params = StdioServerParameters(
                    command="python", 
                    args=["server.py"]
                )
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        # server.py에 add_numbers 도구가 있다면 호출
                        result = await session.call_tool("add_numbers", {"a": a, "b": b})
                        return result.content[0].text
                        
            except Exception as e:
                return f"계산 오류: {str(e)}"
        
        try:
            return asyncio.run(run())
        except Exception as e:
            return f"덧셈 도구 오류 (server.py에 add_numbers 도구가 없을 수 있음): {str(e)}"
    
    def example_time_tool(query: str) -> str:
        """
        시간 조회 도구 (예시) - server.py에 get_time 도구가 있다면 사용 가능
        
        주의: 현재 server.py에는 이 도구가 없으므로 에러가 발생합니다.
        server.py에 다음 도구를 추가하면 사용 가능:
        
        @mcp.tool()
        def get_time() -> dict:
            from datetime import datetime
            return {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        """
        async def run():
            server_params = StdioServerParameters(
                command="python", 
                args=["server.py"]
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # server.py에 get_time 도구가 있다면 호출
                    result = await session.call_tool("get_time")
                    return result.content[0].text
        
        try:
            return asyncio.run(run())
        except Exception as e:
            return f"시간 조회 오류 (server.py에 get_time 도구가 없을 수 있음): {str(e)}"
    
    # 실제 사용 가능한 도구들 (server.py에 있는 도구만)
    active_tools = [
        Tool(
            name="say_hello",
            func=say_hello_tool,
            description="사람 이름을 입력받아 인사말을 생성합니다. 입력: 이름"
        )
    ]
    
    # 예시 도구들 (server.py에 해당 도구가 있으면 주석 해제)
    example_tools = [
        # Tool(
        #     name="add_numbers",
        #     func=example_add_tool,
        #     description="두 숫자를 더합니다. 입력: '10과 20을 더해주세요' 형태"
        # ),
        # Tool(
        #     name="get_time",
        #     func=example_time_tool,
        #     description="현재 시간을 알려줍니다. 매개변수 불필요"
        # )
    ]
    
    print("사용 가능한 도구들:")
    for tool in active_tools:
        print(f"   사용가능 {tool.name}: {tool.description}")
    
    if example_tools:
        print("\n예시 도구들 (server.py에 해당 도구 추가 시 사용 가능):")
        for tool in example_tools:
            print(f"   예시 {tool.name}: {tool.description}")
    
    return active_tools

async def main():
    """
    다중 도구 확장 방식 테스트
    
    실행 과정:
    1. 여러 도구 함수들 생성
    2. LangChain Agent에 모든 도구 등록
    3. 다양한 쿼리로 도구들 테스트
    4. 확장성 확인
    """
    print("=" * 60)
    print("방법 3: 다중 도구 확장 방식")
    print("=" * 60)
    print("이 방식은 실무에서 가장 권장하는 방식입니다.")
    print("확장성이 뛰어나고 유지보수가 쉽습니다.")
    print("새로운 도구 추가가 간단합니다.")
    print("=" * 60)
    
    try:
        # 여러 도구들 생성
        tools = create_server_compatible_tools()
        
        # LangChain Agent 설정
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        # 프롬프트 가져오기
        try:
            prompt = hub.pull("hwchase17/react")
        except Exception as e:
            print(f"LangChain Hub 연결 실패: {e}")
            print("인터넷 연결을 확인하거나 langchainhub 패키지를 설치하세요.")
            return
        
        # Agent 생성 (여러 도구 등록)
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        # 테스트 쿼리들 (현재 server.py에 있는 도구만 사용)
        test_queries = [
            "Bob에게 인사해줘",
            "Charlie에게 안녕하다고 말해줘",
            "David에게 Hello라고 인사해주세요"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n테스트 {i}: {query}")
            print("-" * 40)
            
            try:
                response = await agent_executor.ainvoke({"input": query})
                print(f"결과: {response['output']}")
            except Exception as e:
                print(f"실행 오류: {str(e)}")
            
            print("=" * 60)
        
        # 확장성 테스트 안내
        print("\n확장성 안내:")
        print("server.py에 새로운 도구를 추가하면 이 클라이언트에서도 쉽게 사용할 수 있습니다.")
        print("예시: server.py에 add_numbers, get_time 등의 도구를 추가한 후")
        print("create_server_compatible_tools() 함수에서 해당 도구들의 주석을 해제하세요.")
    
    except Exception as e:
        print(f"전체 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 연결 정리가 자동으로 됨! (각 도구별로 async with 사용)
    print("\n모든 연결이 자동으로 정리되었습니다!")

if __name__ == "__main__":
    print("다중 도구 확장 방식 MCP 클라이언트")
    print("필요 조건:")
    print("- server.py 파일이 현재 디렉토리에 있어야 함")
    print("- OpenAI API 키가 .env 파일에 설정되어 있어야 함")
    print("- 인터넷 연결 (LangChain Hub 접근용)")
    print("-" * 50)
    
    # LangSmith 경고 메시지 비활성화
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    
    asyncio.run(main())
