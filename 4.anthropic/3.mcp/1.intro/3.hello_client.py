import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # MCP 서버 실행 방법을 지정하는 파라미터 설정
    # command: 실행할 프로그램 (여기서는 "python")
    # args: 실행할 파이썬 스크립트 (MCP 서버 코드)
    # 예: hello_server.py → 기본 서버
    server_params = StdioServerParameters(command="python", args=["hello_server.py"])

    # stdio_client() → 지정한 명령으로 MCP 서버를 실행하고
    # 클라이언트에서 서버와 표준 입출력(stdin/stdout) 기반 연결 생성
    async with stdio_client(server_params) as (read, write):
        # ClientSession → MCP 프로토콜을 통해 서버와 대화할 세션 객체
        async with ClientSession(read, write) as session:
            # 서버와 초기화(Handshake) 수행
            # - 버전 교환
            # - 사용 가능한 도구 목록 확인
            await session.initialize()

            # 서버에서 제공하는 "hello" 도구를 호출
            # - 첫 번째 파라미터: 도구 이름
            # - 두 번째 파라미터: 도구 실행에 필요한 인자(딕셔너리)
            result = await session.call_tool("hello", {"name": "John"})
            
            # 결과 출력
            # result.content[0].text → 서버에서 반환한 "Hello, John!" 텍스트
            print(result.content[0].text)  # -> 'Hello, John!'

# asyncio 메인 루프 실행
if __name__ == "__main__":
    asyncio.run(main())


# 내부 동작 순서
# 1. 프로세스 생성: python hello_server.py 실행
# 2. 핸드셰이크: 클라이언트와 서버 간 MCP 프로토콜 협상
# 3. 도구 발견: 서버에서 제공하는 hello 도구 확인
# 4. 도구 호출: hello("John") 원격 실행
# 5. 결과 반환: "Hello, John!" 문자열 반환
# 6. 리소스 정리: 서버 프로세스 종료 및 스트림 닫기
