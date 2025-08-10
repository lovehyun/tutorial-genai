# client1_pydantic.py - Pydantic 기반 커스텀 클래스 방식
"""
방법 1: Pydantic BaseTool을 상속받은 커스텀 클래스 방식

장점:
- 연결을 유지할 수 있음 (이론적으로)
- 객체지향적 설계

단점:
- Pydantic 모델 제약으로 인한 복잡성
- asyncio.run() 중첩 실행 위험
- 연결 관리의 복잡성
- 에러 처리의 어려움
- 많은 보일러플레이트 코드

결론: 복잡하고 불안정해서 실무에서 권장하지 않음
"""

import asyncio
from dotenv import load_dotenv
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

load_dotenv()

class MCPTool(BaseTool):
    """
    MCP 서버와 연결을 유지하는 Pydantic 기반 도구 클래스
    
    주요 문제점들:
    1. Pydantic 모델 제약: 동적 필드 추가 불가능
    2. 연결 상태 관리: 수동으로 연결 시작/종료를 관리해야 함
    3. 에러 처리 복잡: 다양한 예외 상황에 대한 세밀한 처리 필요
    4. asyncio.run() 위험: 이미 실행 중인 이벤트 루프에서 새 루프 생성 시 충돌
    5. 메모리 누수 위험: 연결이 제대로 종료되지 않을 경우
    """
    
    # Pydantic 필수 필드
    name: str = "mcp_say_hello"
    description: str = "입력된 이름으로 인사말을 생성합니다"
    
    # Pydantic 호환 필드 (private 필드로 정의)
    session: Any = None
    server_process: Any = None
    
    class Config:
        arbitrary_types_allowed = True
        # extra 필드 허용
        extra = "allow"
    
    async def start_server(self):
        """
        MCP 서버 시작 및 연결
        
        문제점:
        - 연결 상태를 수동으로 체크해야 함
        - 연결 실패 시 복잡한 에러 처리 필요
        - 메모리 누수 가능성
        """
        if self.session is None:
            try:
                server_params = StdioServerParameters(
                    command="python", 
                    args=["server.py"]  # server.py의 say_hello 도구 사용
                )
                
                # 복잡한 연결 과정
                self.server_process = await stdio_client(server_params).__aenter__()
                read, write = self.server_process
                
                self.session = await ClientSession(read, write).__aenter__()
                await self.session.initialize()
                
            except Exception as e:
                # 연결 실패 시 정리 작업
                await self.cleanup_on_error()
                raise e
    
    async def cleanup_on_error(self):
        """에러 발생 시 정리 작업 (복잡함)"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except:
            pass
        try:
            if self.server_process:
                await self.server_process.__aexit__(None, None, None)
        except:
            pass
        self.session = None
        self.server_process = None
    
    async def stop_server(self):
        """
        MCP 서버 연결 종료
        
        문제점:
        - 수동으로 모든 리소스를 정리해야 함
        - 예외 발생 시 복잡한 처리 필요
        """
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
        except Exception as e:
            print(f"세션 종료 오류: {e}")
        
        try:
            if self.server_process:
                await self.server_process.__aexit__(None, None, None)
                self.server_process = None
        except Exception as e:
            print(f"프로세스 종료 오류: {e}")
    
    def _run(self, name: str) -> str:
        """
        동기 실행 래퍼
        
        주요 문제점: asyncio.run() 중첩 실행
        - 이미 이벤트 루프가 실행 중인 상황에서 새로운 루프를 생성
        - RuntimeError: asyncio.run() cannot be called from a running event loop
        - 예측하기 어려운 동작과 성능 저하
        """
        try:
            return asyncio.run(self._arun(name))
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e):
                return f"이벤트 루프 충돌 오류: {str(e)}"
            return f"런타임 오류: {str(e)}"
        except Exception as e:
            return f"예상치 못한 오류: {str(e)}"
    
    async def _arun(self, name: str) -> str:
        """
        비동기 도구 실행
        
        문제점:
        - 매번 서버 연결 상태를 확인해야 함
        - 복잡한 에러 처리 로직 필요
        """
        try:
            # 연결이 없으면 새로 생성
            await self.start_server()
            
            # server.py의 say_hello 도구 호출
            result = await self.session.call_tool("say_hello", {"name": name})
            
            # server.py는 dict 형태로 반환하므로 적절히 처리
            content = result.content[0]
            if hasattr(content, 'text'):
                return content.text
            else:
                return str(content)
                
        except Exception as e:
            # 에러 발생 시 연결 정리 시도
            await self.cleanup_on_error()
            return f"MCP 호출 오류: {str(e)}"

async def main():
    """
    Pydantic 기반 커스텀 클래스 방식 테스트
    
    실행 과정:
    1. 복잡한 MCPTool 인스턴스 생성
    2. LangChain Agent 설정
    3. 도구 실행 시마다 연결 관리
    4. 수동 리소스 정리
    """
    print("=" * 60)
    print("방법 1: Pydantic 기반 커스텀 클래스 방식")
    print("=" * 60)
    print("경고: 이 방식은 복잡하고 불안정합니다.")
    print("참고: 학습 목적으로만 사용하고, 실무에서는 권장하지 않습니다.")
    print("=" * 60)
    
    # 복잡한 MCPTool 인스턴스 생성
    mcp_tool = MCPTool()
    
    try:
        # LangChain Agent 설정
        llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        
        # 프롬프트 가져오기 (네트워크 의존적)
        try:
            prompt = hub.pull("hwchase17/react")
        except Exception as e:
            print(f"LangChain Hub 연결 실패: {e}")
            print("해결책: 인터넷 연결을 확인하거나 langchainhub 패키지를 설치하세요.")
            return
        
        # Agent 생성
        agent = create_react_agent(llm, [mcp_tool], prompt)
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=[mcp_tool], 
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
        
        # 테스트 실행
        test_queries = [
            "John에게 인사해줘",
            "Alice에게 안녕하다고 말해줘"
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
    
    except Exception as e:
        print(f"전체 실행 오류: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 복잡한 리소스 정리 과정
        print("\n리소스 정리 중...")
        try:
            await mcp_tool.stop_server()
            print("리소스 정리 완료")
        except Exception as e:
            print(f"리소스 정리 중 오류: {e}")

if __name__ == "__main__":
    print("Pydantic 기반 MCP 클라이언트 (복잡한 방식)")
    print("필요 조건:")
    print("- server.py 파일이 현재 디렉토리에 있어야 함")
    print("- OpenAI API 키가 .env 파일에 설정되어 있어야 함") 
    print("- 인터넷 연결 (LangChain Hub 접근용)")
    print("-" * 50)
    
    asyncio.run(main())
