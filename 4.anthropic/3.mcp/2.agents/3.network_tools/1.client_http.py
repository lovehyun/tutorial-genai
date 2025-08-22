import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    print("=" * 50)
    print("HTTP MCP 클라이언트 시작")
    print("=" * 50)
    print("서버 연결 중: http://localhost:8000/mcp")
    
    try:
        # Streamable HTTP로 연결
        async with streamablehttp_client("http://localhost:8000/mcp") as (read, write, _):
            async with ClientSession(read, write) as session:
                
                # 서버와 핸드셰이크 수행
                await session.initialize()
                print("서버 연결 성공!")
                
                # 서버 정보 조회 및 출력
                print(f"\nMCP 서버 정보")
                print(f"연결 상태: {'연결됨' if session else '연결 실패'}")
                
                # 사용 가능한 도구 목록 조회
                print(f"\n사용 가능한 도구:")
                try:
                    tools_response = await session.list_tools()
                    if tools_response and hasattr(tools_response, 'tools') and tools_response.tools:
                        for i, tool in enumerate(tools_response.tools, 1):
                            print(f"   {i}. {tool.name}")
                            if hasattr(tool, 'description'):
                                print(f"      설명: {tool.description}")
                            
                            # 매개변수 정보 출력
                            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                                schema = tool.inputSchema
                                if isinstance(schema, dict) and 'properties' in schema:
                                    print(f"      매개변수:")
                                    for param_name, param_info in schema['properties'].items():
                                        param_type = param_info.get('type', 'unknown')
                                        param_desc = param_info.get('description', '설명 없음')
                                        required = param_name in schema.get('required', [])
                                        required_mark = " (필수)" if required else " (선택)"
                                        print(f"         - {param_name} ({param_type}){required_mark}: {param_desc}")
                            print()
                    else:
                        print("   사용 가능한 도구가 없습니다.")
                except Exception as e:
                    print(f"   도구 목록 조회 실패: {e}")
                
                # 도구 실행 데모
                print(f"\n도구 실행 데모:")
                
                # 도구 1: hello 도구 호출
                print("1. hello 도구 호출 중...")
                res1 = await session.call_tool("hello", {"name": "Alice"})
                print(f"   결과: {res1.content[0].text}")

                # 도구 2: add 도구 호출
                print("2. add 도구 호출 중...")
                res2 = await session.call_tool("add", {"a": 15, "b": 25})
                print(f"   결과: {res2.content[0].text}")

                # 도구 3: now 도구 호출
                print("3. now 도구 호출 중...")
                res3 = await session.call_tool("now")
                print(f"   결과: {res3.content[0].text}")
                
                print(f"\n모든 도구 실행 완료!")
                
    except Exception as e:
        print(f"연결 실패: {e}")
        print("서버가 실행 중인지 확인하세요: python server_http.py")
        
        # 에러 상세 정보
        import traceback
        print(f"\n에러 상세:")
        print(traceback.format_exc())

if __name__ == "__main__":
    print("HTTP MCP 클라이언트를 시작합니다...")
    print("서버가 실행 중이어야 합니다: python server_http.py")
    print("-" * 50)
    
    asyncio.run(main())
