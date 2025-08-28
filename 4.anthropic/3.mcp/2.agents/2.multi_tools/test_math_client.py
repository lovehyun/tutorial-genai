# math_client.py
import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "math_server.py"  # 서버 스크립트 파일명

def _extract_text(result) -> str:
    """MCP call_tool 응답에서 텍스트를 안전하게 추출"""
    if hasattr(result, "content") and result.content:  # 'content' 라는 속성이 있고 빈 리스트가 아닐 경우
        item = result.content[0]
        return getattr(item, "text", None) or str(item)  # text 속성이 있으면 그 값을 가져옴, 아니면 문자열 파싱
    return ""

async def main():
    # 동일한 파이썬 인터프리터로 서버 실행 (윈도우/가상환경 호환성 ↑)
    params = StdioServerParameters(command=sys.executable, args=[SERVER_FILE])

    # stdio 기반으로 서버 프로세스 실행 및 세션 생성
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) 도구 목록 확인
            tools_result = await session.list_tools()
            print("사용 가능 도구:")
            for t in tools_result.tools:
                print(f"  - {t.name}: {t.description}")

            # 2) hello 호출
            hello_res = await session.call_tool("hello", {"name": "Alice"})
            print("hello 결과:", _extract_text(hello_res))

            # 3) add 호출
            add_res = await session.call_tool("add", {"a": 5, "b": 7})
            print("add 결과:", _extract_text(add_res))

if __name__ == "__main__":
    asyncio.run(main())
