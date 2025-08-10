from mcp.server.fastmcp import FastMCP

# FastMCP 객체 생성
# - "HelloWorld"는 MCP 서버 이름(클라이언트가 식별할 수 있도록 사용됨)
mcp = FastMCP("HelloWorld")

# MCP 도구(tool) 등록
# - @mcp.tool() 데코레이터를 사용하면 클라이언트에서 호출 가능한 "명령"이 됨
# - 도구 이름은 기본적으로 함수 이름(여기서는 "hello")
# - name: 입력 매개변수 (기본값 "World")
# - 반환값: 간단한 문자열
@mcp.tool()
def hello(name: str = "World") -> str:
    return f"Hello, {name}!"

# MCP 서버 실행
# - 표준 입출력(stdin/stdout)을 통해 JSON-RPC 기반 MCP 프로토콜로 통신
# - 실행 흐름:
#   1. 클라이언트 연결 및 초기화(initialize)
#   2. 도구 목록 전송(hello 포함)
#   3. 클라이언트가 call_tool("hello", {...}) 요청 시 hello 함수 실행
#   4. 실행 결과를 JSON-RPC 응답으로 반환
if __name__ == "__main__":
    mcp.run()
