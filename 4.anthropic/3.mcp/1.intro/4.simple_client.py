import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("==================================================")
    print("MCP 디버깅 시작")
    print("==================================================")
    
    # 기존 로그 파일 삭제
    if os.path.exists("proxy_debug.log"):
        os.remove("proxy_debug.log")
    
    # 프록시를 통해 서버에 연결
    server_params = StdioServerParameters(
        command="python", 
        # args=["simple_server.py"]
        args=["simple_proxy.py", "simple_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("[CLIENT] 초기화 중...")
                
                # 타임아웃 설정
                init_result = await asyncio.wait_for(session.initialize(), timeout=5.0)
                print(f"[CLIENT] 연결 성공: {init_result.serverInfo.name}")
                
                print("[CLIENT] 도구 목록 조회 중...")
                tools_result = await asyncio.wait_for(session.list_tools(), timeout=5.0)
                tool_names = [tool.name for tool in tools_result.tools]
                print(f"[CLIENT] 사용 가능한 도구: {tool_names}")
                
                print("[CLIENT] hello 도구 호출 중...")
                result = await asyncio.wait_for(
                    session.call_tool("hello", {"name": "John"}), 
                    timeout=5.0
                )
                print(f"[CLIENT] 결과: {result.content[0].text}")
                
                print("[CLIENT] 두 번째 호출...")
                result2 = await asyncio.wait_for(
                    session.call_tool("hello", {"name": "Alice"}), 
                    timeout=5.0
                )
                print(f"[CLIENT] 결과: {result2.content[0].text}")
                
    except asyncio.TimeoutError:
        print("[CLIENT] 타임아웃 발생!")
    except Exception as e:
        print(f"[CLIENT] 에러: {e}")
        import traceback
        traceback.print_exc()
    
    print("[CLIENT] 완료!")
    
    
    # 프록시 디버그 로그 출력
    print("\n" + "="*50)
    print("프록시 디버그 로그:")
    print("="*50)
    
    try:
        # 잠깐 기다려서 로그가 완전히 기록되도록
        await asyncio.sleep(0.5)
        
        if os.path.exists("proxy_debug.log"):
            with open("proxy_debug.log", "r", encoding="utf-8") as f:
                content = f.read()
                print(content)
        else:
            print("로그 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"로그 파일 읽기 에러: {e}")

if __name__ == "__main__":
    asyncio.run(main())
