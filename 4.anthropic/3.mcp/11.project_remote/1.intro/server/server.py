# 원격 MCP 서버 (HTTP 기반)

# MCP가 자동으로 생성하는 것들:
# - 함수 이름 → 도구 이름
# - docstring → 도구 설명  
# - 타입 힌트 → 매개변수 타입
# - 기본값 → 선택적 매개변수

# 표준 MCP 서버 (docstring + typehint 방식)
# 공식 MCP SDK 서버 (심플 버전)

import sys
from datetime import datetime
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

# 공식 MCP SDK 서버 인스턴스 생성
mcp = FastMCP("SimpleRemoteServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    """인사말을 생성합니다.
    
    Args:
        name: 인사할 대상의 이름 (기본값: "World")
    
    Returns:
        str: 생성된 인사말
    """
    return f"Hello, {name}! (from remote server)"

@mcp.tool()
def add(a: float, b: float) -> float:
    """두 숫자를 더합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        float: 두 숫자의 합
    """
    return a + b

@mcp.tool()
def current_time() -> str:
    """현재 시간을 조회합니다.
    
    Returns:
        str: 현재 서버 시간 (YYYY-MM-DD HH:MM:SS 형식)
    """
    return f"Remote server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool()
def weather(city: str) -> Dict[str, Any]:
    """도시의 날씨 정보를 조회합니다 (가상 데이터).
    
    Args:
        city: 날씨를 조회할 도시 이름
    
    Returns:
        Dict[str, Any]: 날씨 정보 딕셔너리 (도시명, 온도, 상태, 습도, 출처 포함)
    """
    return {
        "city": city,
        "temperature": "22°C",
        "condition": "맑음",
        "humidity": "60%",
        "source": "remote_server"
    }

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """두 숫자를 곱합니다.
    
    Args:
        a: 첫 번째 숫자
        b: 두 번째 숫자
    
    Returns:
        float: 두 숫자의 곱
    """
    return a * b

@mcp.tool()
def get_server_info() -> Dict[str, str]:
    """서버 정보를 반환합니다.
    
    Returns:
        Dict[str, str]: 서버 상태 및 메타데이터
    """
    return {
        "name": "SimpleRemoteServer",
        "status": "running",
        "framework": "Official MCP SDK",
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def echo(message: str) -> str:
    """메시지를 그대로 반환합니다.
    
    Args:
        message: 반환할 메시지
    
    Returns:
        str: 입력받은 메시지
    """
    return f"Echo: {message}"

if __name__ == "__main__":
    # 명령행 인자로 모드 선택
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--stdio":
            print("STDIO 서버 시작")
            mcp.run(transport="stdio")
        elif mode == "--http":
            print("HTTP 서버 시작")
            mcp.run(transport="streamable-http")
    else:
        print("사용법:")
        print("  python server.py --stdio  # STDIO 서버")
        print("  python server.py --http   # HTTP 서버")
