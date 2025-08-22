# utility_client.py
import sys
import asyncio
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "utility_server.py"  # 테스트할 서버 파일명

def _extract_text(result) -> str:
    """MCP call_tool 응답에서 텍스트를 안전하게 추출"""
    if hasattr(result, "content") and result.content:
        item = result.content[0]
        return getattr(item, "text", None) or str(item)
    return ""

async def main():
    # 같은 파이썬 인터프리터로 서버 실행 (가상환경/윈도우 호환)
    params = StdioServerParameters(command=sys.executable, args=[SERVER_FILE])

    try:
        # stdio 기반 서버 프로세스 실행 → MCP 세션 생성
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 1) 도구 목록 확인
                tools_result = await session.list_tools()
                print("사용 가능 도구:")
                for t in tools_result.tools:
                    print(f"  - {t.name}: {t.description}")

                # 2) current_time 호출
                res_time = await session.call_tool("current_time", {})
                print("current_time 결과:", _extract_text(res_time))

                # 3) weather 호출 (도시 지정)
                res_weather_busan = await session.call_tool("weather", {"city": "부산"})
                print("weather(부산) 결과:", _extract_text(res_weather_busan))

                # 4) weather 호출 (미정 도시 → 서버의 기본/없는 도시 처리 확인)
                res_weather_jeju = await session.call_tool("weather", {"city": "제주"})
                print("weather(제주) 결과:", _extract_text(res_weather_jeju))

                # 5) weather 호출 (파라미터 생략 → 기본값 '서울')
                res_weather_default = await session.call_tool("weather", {})
                print("weather(기본) 결과:", _extract_text(res_weather_default))

    except Exception as e:
        print("클라이언트 실행 중 예외 발생:", e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
