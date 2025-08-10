# client2_simple_function.py - 간단한 함수 기반 방식
"""
방법 2: 간단한 함수 기반 방식 (매번 새 연결)

장점:
- 코드가 간단하고 이해하기 쉬움
- 연결 관리가 자동화됨 (with 문 사용)
- 각 호출이 독립적이라 안정적
- 에러 처리가 간단함
- 메모리 누수 위험 없음

단점:
- 매번 새로운 연결을 생성 (약간의 오버헤드)
- asyncio.run()을 여전히 사용 (이벤트 루프 중첩 위험)

결론: 방법 1보다 훨씬 안정적이고 실용적
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

# LangSmith 경고 메시지 비활성화
os.environ["LANGCHAIN_TRACING_V2"] = "false"
# langchain hub를 사용할 때 LangSmith 추적 기능이 자동으로 활성화됨
# LangSmith는 LangChain의 모니터링/추적 서비스
# API 키가 없으면 경고 메시지 출력


def create_simple_mcp_tool():
    """
    간단한 MCP 도구 생성 함수
    
    특징:
    - 함수 기반으로 클래스보다 단순함
    - 연결 관리가 자동화됨 (async with 사용)
    - 각 호출마다 새로운 연결 생성 (독립적, 안전함)
    - 에러 처리가 간단함
    """
    
    def call_mcp_say_hello(name: str) -> str:
        """
        server.py의 say_hello 도구를 호출하는 래퍼 함수
        
        동작 과정:
        1. 새로운 MCP 서버 프로세스 시작
        2. 세션 초기화
        3. 도구 호출
        4. 결과 반환
        5. 자동으로 연결 정리 (async with)
        
        장점:
        - 연결 관리가 자동화됨
        - 각 호출이 독립적
        - 메모리 누수 없음
        """
        async def run():
            # MCP 서버 매개변수 설정
            server_params = StdioServerParameters(
                command="python", 
                args=["server.py"]  # server.py의 say_hello 도구 사용
            )
            
            # 자동 연결 관리: 블록 종료 시 자동으로 정리됨
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # 세션 초기화
                    await session.initialize()
                    
                    # server.py의 say_hello 도구 호출
                    result = await session.call_tool("say_hello", {"name": name})
                    
                    # 결과 처리: server.py는 dict 형태로 반환
                    # MCP 프로토콜에 의해 텍스트로 변환되어 전달됨
                    return result.content[0].text
        
        try:
            # 여전히 asyncio.run() 사용 (이벤트 루프 중첩 위험)
            # 하지만 방법 1보다는 훨씬 안정적
            return asyncio.run(run())
        except Exception as e:
            # 간단한 에러 처리
            return f"MCP 호출 에러: {str(e)}"
    
    # LangChain Tool 객체 생성
    return Tool(
        name="say_hello",
        func=call_mcp_say_hello,
        description="MCP 서버를 통해 인사말을 생성합니다. 입력: 사람 이름"
    )

async def main():
    """
    간단한 함수 기반 방식 테스트
    
    실행 과정:
    1. 간단한 도구 함수 생성
    2. LangChain Agent 설정
    3. 도구 실행 (연결 관리 자동화)
    4. 결과 확인
    """
    print("=" * 60)
    print("방법 2: 간단한 함수 기반 방식 (매번 새 연결)")
    print("=" * 60)
    print("정보: 이 방식은 간단하고 안정적입니다.")
    print("참고: 실무에서 사용하기 적합합니다.")
    print("주의: 매번 새 연결을 생성하므로 약간의 오버헤드가 있습니다.")
    print("=" * 60)
    
    try:
        # 간단한 도구 생성 (한 줄!)
        simple_tool = create_simple_mcp_tool()
        
        # LangChain Agent 설정
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        # 프롬프트 가져오기
        try:
            prompt = hub.pull("hwchase17/react")
        except Exception as e:
            print(f"LangChain Hub 연결 실패: {e}")
            print("해결책: 인터넷 연결을 확인하거나 langchainhub 패키지를 설치하세요.")
            return
        
        # Agent 생성 (간단함)
        agent = create_react_agent(llm, [simple_tool], prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=[simple_tool],
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        # 테스트 실행
        test_queries = [
            "Alice에게 인사해줘",
            "Bob에게 Hello라고 말해줘",
            "Charlie에게 안녕하세요라고 인사해주세요"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n테스트 {i}: {query}")
            print("-" * 40)
            
            try:
                # 각 호출마다 새로운 MCP 연결이 생성됨
                response = await agent_executor.ainvoke({"input": query})
                print(f"결과: {response['output']}")
            except Exception as e:
                print(f"실행 오류: {str(e)}")
            
            print("=" * 60)
    
    except Exception as e:
        print(f"전체 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 연결 정리가 자동으로 됨! (async with 덕분)
    print("\n연결 정리가 자동으로 완료되었습니다!")

if __name__ == "__main__":
    print("간단한 함수 기반 MCP 클라이언트")
    print("필요 조건:")
    print("- server.py 파일이 현재 디렉토리에 있어야 함")
    print("- OpenAI API 키가 .env 파일에 설정되어 있어야 함")
    print("- 인터넷 연결 (LangChain Hub 접근용)")
    print("-" * 50)
    
    asyncio.run(main())
