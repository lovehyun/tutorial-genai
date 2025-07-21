import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(command="python", args=["hello_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("hello", {"name": "John"})
            print(result.content[0].text)  # → 'Hello, John!'

if __name__ == "__main__":
    asyncio.run(main())

# 내부 동작 순서
# 1. 프로세스 생성: python hello_server.py 실행
# 2. 핸드셰이크: 클라이언트와 서버 간 MCP 프로토콜 협상
# 3. 도구 발견: 서버에서 제공하는 hello 도구 확인
# 4. 도구 호출: hello("John") 원격 실행
# 5. 결과 반환: "Hello, John!" 문자열 반환
# 6. 리소스 정리: 서버 프로세스 종료 및 스트림 닫기
