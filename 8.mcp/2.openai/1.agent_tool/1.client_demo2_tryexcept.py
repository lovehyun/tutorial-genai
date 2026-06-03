# 전체 시스템 아키텍처
# 프로세스 구조
# ┌─────────────────┐    stdio    ┌─────────────────┐
# │   클라이언트     │◄───────────►│   서버 프로세스  │
# │   (client.py)   │   (pipe)    │   (server.py)   │
# │                 │             │                 │
# │ ┌─────────────┐ │             │ ┌─────────────┐ │
# │ │ClientSession│ │             │ │  FastMCP    │ │
# │ │             │ │             │ │             │ │
# │ │ - 요청 관리  │ │             │ │ - 도구 등록  │ │
# │ │ - 응답 매칭  │ │             │ │ - 스키마 생성│ │
# │ │ - 에러 처리  │ │             │ │ - 요청 처리  │ │
# │ └─────────────┘ │             │ └─────────────┘ │
# └─────────────────┘             └─────────────────┘

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # ===== 서버 프로세스 설정 =====
    # 별도 Python 프로세스에서 server.py를 실행하기 위한 매개변수
    # command: 실행할 명령어 (python)
    # args: 명령어에 전달할 인수 (server.py)
    server_params = StdioServerParameters(
        command="python", args=["server.py"]
    )

    # ===== 서버 프로세스 시작 및 통신 채널 설정 =====
    # stdio_client: 표준 입출력을 통한 서버와의 통신 채널 생성
    # read: 서버로부터 메시지를 받는 스트림
    # write: 서버로 메시지를 보내는 스트림
    async with stdio_client(server_params) as (read, write):
        
        # ===== MCP 세션 시작 =====
        # ClientSession: MCP 프로토콜을 구현하는 클라이언트 세션
        # 요청/응답 매칭, 알림 처리, 진행률 추적 등을 담당
        async with ClientSession(read, write) as session:
            
            # ===== 서버와 핸드셰이크 수행 =====
            # 서버의 capabilities 확인
            # 사용 가능한 도구 목록 조회
            # 프로토콜 버전 협상
            await session.initialize()

            # ===== 서버 정보 조회 및 출력 =====
            print("=" * 50)
            print("MCP 서버 정보")
            print("=" * 50)
            
            # 1. 연결 상태 확인
            print(f"연결 상태: {'연결됨' if session else '연결 실패'}")
            
            # 2. 사용 가능한 도구 목록 조회
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
                # 에러 상세 정보 출력
                import traceback
                print(f"   에러 상세: {traceback.format_exc()}")
            
            print(f"\n도구 실행 데모:")
            # ===== 도구 1: hello 도구 호출 =====
            # 매개변수: {"name": "John"}를 JSON으로 직렬화하여 전송
            # 서버에서 hello("John") 함수 실행
            # 결과: ToolResult 객체로 반환
            res1 = await session.call_tool("hello", {"name": "John"})
            print(" - hello tool: ", res1.content[0].text)  # → "Hello, John!"

            # ===== 도구 2: add 도구 호출 =====
            # 두 개의 필수 매개변수 전달
            # 서버에서 add(5, 7) 함수 실행
            res2 = await session.call_tool("add", {"a": 5, "b": 7})
            print(" - add tool: ", res2.content[0].text)    # → "12"

            # ===== 도구 3: now 도구 호출 =====
            # 매개변수 없는 도구 호출
            # 서버에서 now() 함수 실행
            res3 = await session.call_tool("now")
            print(" - now tool: ", res3.content[0].text)   # → "지금 시간은 2025-07-20 14:30:45 입니다."

    # ===== 자동 리소스 정리 =====
    # async with 블록이 끝나면:
    # 1. 서버 프로세스 종료
    # 2. 통신 스트림 닫기
    # 3. 메모리 정리

if __name__ == "__main__":
    # 비동기 메인 함수 실행
    asyncio.run(main())


#  클라이언트의 실행 흐름
# 
# 1. 프로세스 시작     python server.py 실행
#          ↓
# 2. 통신 채널 설정    stdin/stdout 파이프 생성
#          ↓
# 3. MCP 세션 시작     프로토콜 핸드셰이크
#          ↓
# 4. 도구 발견        서버의 도구 목록 조회
#          ↓
# 5. 도구 호출        순차적으로 3개 도구 실행
#          ↓
# 6. 결과 출력        각 도구의 결과를 콘솔에 출력
#          ↓
# 7. 정리            서버 프로세스 종료 및 리소스 해제

# 통신 프로토콜 (JSON-RPC over stdio)
# 클라이언트 요청:
# {
#   "jsonrpc": "2.0",
#   "id": 1,
#   "method": "tools/call",
#   "params": {
#     "name": "hello",
#     "arguments": {"name": "John"}
#   }
# }
#
# 서버 응답:
# {
#   "jsonrpc": "2.0",
#   "id": 1,
#   "result": {
#     "content": [
#       {
#         "type": "text",
#         "text": "Hello, John!"
#       }
#     ]
#   }
# }
