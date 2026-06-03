# 공식 MCP SDK 클라이언트 (심플 버전)

import asyncio
import os
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

class MCPClient:
    """공식 MCP SDK 클라이언트"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
    
    async def test_all_tools(self):
        """모든 도구 자동 테스트"""
        print(f"MCP 서버 연결: {self.server_url}")
        print("=" * 50)
        
        async with streamablehttp_client(self.server_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("서버 연결 성공")
                
                # 도구 목록 조회
                tools_result = await session.list_tools()
                tools = tools_result.tools
                
                print(f"\n사용 가능한 도구 ({len(tools)}개):")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                if not tools:
                    print("사용 가능한 도구가 없습니다.")
                    return
                
                print("\n" + "=" * 50)
                print("도구 테스트 시작")
                print("=" * 50)
                
                # 테스트 케이스
                test_cases = [
                    ("hello", {"name": "MCP User"}, "인사말 테스트"),
                    ("hello", {}, "기본값 테스트"),
                    ("add", {"a": 15.5, "b": 24.3}, "덧셈 테스트"),
                    ("multiply", {"a": 7, "b": 8}, "곱셈 테스트"),
                    ("current_time", {}, "시간 조회 테스트"),
                    ("weather", {"city": "Seoul"}, "날씨 조회 테스트"),
                    ("get_server_info", {}, "서버 정보 테스트"),
                    ("echo", {"message": "Hello MCP"}, "에코 테스트")
                ]
                
                for i, (tool_name, params, description) in enumerate(test_cases, 1):
                    print(f"\n테스트 {i}/{len(test_cases)}: {description}")
                    print(f"  도구: {tool_name}")
                    print(f"  매개변수: {params}")
                    
                    try:
                        result = await session.call_tool(tool_name, params)
                        
                        if hasattr(result, 'content') and result.content:
                            for content_item in result.content:
                                if hasattr(content_item, 'text'):
                                    print(f"  결과: {content_item.text}")
                                else:
                                    print(f"  결과: {content_item}")
                        else:
                            print(f"  결과: {result}")
                            
                    except Exception as e:
                        print(f"  오류: {e}")
                    
                    print("  " + "-" * 40)
                
                print("\n모든 테스트 완료")

async def interactive_mode():
    """대화형 모드"""
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    
    print("대화형 MCP 클라이언트")
    print("=" * 40)
    
    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 도구 목록 표시
            tools_result = await session.list_tools()
            tools = tools_result.tools
            
            print("사용 가능한 명령어:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n사용 예시:")
            print("  hello Alice")
            print("  add 10 20")
            print("  weather Seoul")
            print("  time")
            print("  quit (종료)")
            print("-" * 40)
            
            while True:
                user_input = input("\n[사용자] 명령: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("대화형 모드를 종료합니다.")
                    break
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                
                if cmd == "hello":
                    name = parts[1] if len(parts) > 1 else "World"
                    result = await session.call_tool("hello", {"name": name})
                    print_result("[서버]", result)
                    
                elif cmd == "add":
                    if len(parts) >= 3:
                        try:
                            a, b = float(parts[1]), float(parts[2])
                            result = await session.call_tool("add", {"a": a, "b": b})
                            print(f"[서버] {a} + {b} = ", end="")
                            print_result("", result)
                        except ValueError:
                            print("[오류] 숫자를 입력하세요")
                    else:
                        print("[오류] 사용법: add 숫자1 숫자2")
                        
                elif cmd == "multiply":
                    if len(parts) >= 3:
                        try:
                            a, b = float(parts[1]), float(parts[2])
                            result = await session.call_tool("multiply", {"a": a, "b": b})
                            print(f"[서버] {a} × {b} = ", end="")
                            print_result("", result)
                        except ValueError:
                            print("[오류] 숫자를 입력하세요")
                    else:
                        print("[오류] 사용법: multiply 숫자1 숫자2")
                        
                elif cmd in ["time", "current_time"]:
                    result = await session.call_tool("current_time", {})
                    print_result("[서버]", result)
                    
                elif cmd == "weather":
                    city = parts[1] if len(parts) > 1 else "Seoul"
                    result = await session.call_tool("weather", {"city": city})
                    print_result("[서버]", result)
                    
                elif cmd == "info":
                    result = await session.call_tool("get_server_info", {})
                    print_result("[서버]", result)
                    
                elif cmd == "echo":
                    message = " ".join(parts[1:]) if len(parts) > 1 else "Hello!"
                    result = await session.call_tool("echo", {"message": message})
                    print_result("[서버]", result)
                    
                else:
                    print(f"[오류] 알 수 없는 명령어: {cmd}")

def print_result(prefix: str, result):
    """결과 출력 함수"""
    if hasattr(result, 'content') and result.content:
        for content_item in result.content:
            if hasattr(content_item, 'text'):
                print(f"{prefix} {content_item.text}")
            else:
                print(f"{prefix} {content_item}")
    else:
        print(f"{prefix} {result}")

async def main():
    """메인 함수"""
    print("MCP 클라이언트 테스트")
    print("모드를 선택하세요:")
    print("1. 자동 테스트")
    print("2. 대화형 테스트")
    
    choice = input("선택 (1/2): ").strip()
    server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    
    if choice == "2":
        await interactive_mode()
    else:
        client = MCPClient(server_url)
        await client.test_all_tools()

if __name__ == "__main__":
    asyncio.run(main())
