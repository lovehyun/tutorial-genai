# server2.py - MCP 서버 (개선된 버전)
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# MCP 서버 생성
mcp = FastMCP("ImprovedServer")

@mcp.tool()
def say_hello(name: str) -> str:
    """
    사용자에게 개인화된 인사말을 생성합니다.
    
    Args:
        name (str): 인사할 대상의 이름
    
    Returns:
        str: 인사말 (JSON이 아닌 일반 텍스트)
    """
    # JSON 대신 직접 텍스트 반환
    return f"안녕하세요, {name}님! 좋은 하루 되세요!"

@mcp.tool()
def add(a: int, b: int) -> str:
    """
    두 정수를 더합니다.
    
    Args:
        a (int): 첫 번째 숫자
        b (int): 두 번째 숫자
    
    Returns:
        str: 계산 결과
    """
    result = a + b
    return f"{a} + {b} = {result}"

@mcp.tool()
def now() -> str:
    """
    현재 시간을 반환합니다.
    
    Returns:
        str: 현재 시간
    """
    current_time = datetime.now()
    return f"현재 시간: {current_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')}"

# 추가 도구들
@mcp.tool()
def multiply(a: int, b: int) -> str:
    """
    두 숫자를 곱합니다.
    
    Args:
        a (int): 첫 번째 숫자
        b (int): 두 번째 숫자
    
    Returns:
        str: 곱셈 결과
    """
    result = a * b
    return f"{a} × {b} = {result}"

@mcp.tool()
def get_day_of_week() -> str:
    """
    오늘이 무슨 요일인지 알려줍니다.
    
    Returns:
        str: 요일 정보
    """
    days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    today = datetime.now().weekday()
    return f"오늘은 {days[today]}입니다."

# 서버 실행
if __name__ == "__main__":
    print("MCP 서버 시작 (STDIO 모드)")
    print("사용 가능한 도구:")
    print("- say_hello: 인사말 생성")
    print("- add: 덧셈 계산")
    print("- multiply: 곱셈 계산") 
    print("- now: 현재 시간")
    print("- get_day_of_week: 요일 정보")
    print("-" * 30)
    
    # STDIO 모드로 실행 (LangChain과 통신용)
    mcp.run(transport="stdio")
