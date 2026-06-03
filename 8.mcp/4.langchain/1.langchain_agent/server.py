# MCP (Model Context Protocol) 서버를 위한 FastMCP 라이브러리 import
from mcp.server.fastmcp import FastMCP

# ===== MCP 서버 인스턴스 생성 =====
# "HelloLangchain"이라는 이름으로 MCP 서버 생성
# 이 이름은 클라이언트가 서버를 식별할 때 사용됩니다
mcp = FastMCP("HelloLangchain")

# ===== 도구(Tool) 정의 =====
@mcp.tool()  # 이 데코레이터가 함수를 MCP 도구로 등록합니다
def say_hello(name: str) -> dict:
    """
    사용자 이름을 받아서 인사말을 생성하는 도구
    
    Args:
        name (str): 인사할 대상의 이름
    
    Returns:
        dict: 인사말이 포함된 딕셔너리
              형태: {"greeting": "Hello, {name}!"}
    
    Note:
        이 함수의 docstring은 MCP 클라이언트에게 도구 설명으로 제공됩니다.
        타입 힌트(name: str, -> dict)는 MCP 스키마 생성에 사용됩니다.
    """
    return {"greeting": f"Hello, {name}!"}

# ===== 서버 실행 =====
if __name__ == "__main__":
    # MCP 서버를 실행합니다
    # 기본값: transport="stdio" (표준 입출력을 통한 통신)
    # 
    # 다른 transport 옵션들:
    # - "stdio": 표준 입출력 (기본값) - 로컬 프로세스 통신용
    # - "streamable-http": HTTP 기반 - 네트워크 통신용  
    # - "sse": Server-Sent Events - 웹 브라우저 통신용 (deprecated)
    #
    # 예시:
    # mcp.run()                                    # stdio (기본값)
    # mcp.run(transport="stdio")                   # stdio 명시적 지정
    # mcp.run(transport="streamable-http")         # HTTP 서버로 실행
    
    mcp.run()  # 기본값인 stdio transport로 서버 시작
