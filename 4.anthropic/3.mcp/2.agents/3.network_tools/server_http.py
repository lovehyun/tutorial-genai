from mcp.server.fastmcp import FastMCP
from datetime import datetime

# ===== MCP 서버 인스턴스 생성 =====
mcp = FastMCP("HTTPMultiToolServer")

# ===== 도구 1: 인사말 생성기 =====
@mcp.tool()
def hello(name: str = "World") -> str:
    """
    사용자에게 개인화된 인사말을 생성하는 도구
    
    매개변수:
        name (str): 인사할 대상의 이름 (기본값: "World")
    
    반환값:
        str: "Hello, {name}!" 형태의 인사말
    """
    return f"Hello, {name}!"

# ===== 도구 2: 덧셈 계산기 =====
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    두 정수의 덧셈을 수행하는 계산기 도구
    
    매개변수:
        a (int): 첫 번째 숫자 (필수)
        b (int): 두 번째 숫자 (필수)
    
    반환값:
        int: a + b의 결과
    """
    return a + b

# ===== 도구 3: 현재 시간 조회 =====
@mcp.tool()
def now() -> str:
    """
    현재 시간을 한국어로 포맷하여 반환하는 도구
    
    매개변수: 없음
    
    반환값:
        str: "지금 시간은 YYYY-MM-DD HH:MM:SS 입니다." 형태의 시간 정보
    """
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")

# ===== HTTP 서버 실행 =====
if __name__ == "__main__":
    print("=" * 50)
    print("HTTP MCP 서버 시작")
    print("=" * 50)
    print("서버가 기본 포트(8000)에서 시작됩니다")
    print("종료하려면 Ctrl+C를 누르세요")
    print("=" * 50)
    
    # HTTP 서버로 실행
    mcp.run(transport="streamable-http")
