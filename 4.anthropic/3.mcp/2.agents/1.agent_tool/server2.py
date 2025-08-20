from mcp.server.fastmcp import FastMCP
from datetime import datetime
import random
import math
import os

# MCP 도구에서 주석은 매우 중요한 역할을 합니다! 무시되지 않고 실제로 활용됩니다.
# 함수 docstring → 도구 설명(description)

# ===== MCP 서버 인스턴스 생성 =====
# "MultiToolServer"라는 이름의 MCP 서버 생성
# 이 이름은 클라이언트가 서버를 식별하는 데 사용됨
mcp = FastMCP("MultiToolServer")

# ===== 기존 도구들 =====

@mcp.tool()  # 함수를 MCP 도구로 등록하는 데코레이터
def hello(name: str = "World") -> str:
    """
    사용자에게 개인화된 인사말을 생성하는 도구
    
    매개변수:
        name (str): 인사할 대상의 이름 (기본값: "World")
    
    반환값:
        str: "Hello, {name}!" 형태의 인사말
    """
    return f"Hello, {name}!"

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

@mcp.tool()
def now() -> str:
    """
    현재 시간을 한국어로 포맷하여 반환하는 도구
    
    매개변수: 없음
    
    반환값:
        str: "지금 시간은 YYYY-MM-DD HH:MM:SS 입니다." 형태의 시간 정보
    """
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")

# ===== 추가된 계산기 도구들 =====

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    두 정수의 곱셈을 수행하는 계산기 도구
    
    매개변수:
        a (int): 첫 번째 숫자 (필수)
        b (int): 두 번째 숫자 (필수)
    
    반환값:
        int: a × b의 결과
    """
    return a * b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    두 정수의 뺄셈을 수행하는 계산기 도구
    
    매개변수:
        a (int): 첫 번째 숫자 (필수)
        b (int): 두 번째 숫자 (필수)
    
    반환값:
        int: a - b의 결과
    """
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> str:
    """
    두 수의 나눗셈을 수행하는 계산기 도구
    
    매개변수:
        a (float): 나누어질 숫자 (필수)
        b (float): 나누는 숫자 (필수, 0이면 안됨)
    
    반환값:
        str: a ÷ b의 결과 또는 오류 메시지
    """
    if b == 0:
        return "오류: 0으로 나눌 수 없습니다."
    result = a / b
    return f"{a} ÷ {b} = {result}"

@mcp.tool()
def power(base: float, exponent: float) -> str:
    """
    거듭제곱을 계산하는 도구
    
    매개변수:
        base (float): 밑 (필수)
        exponent (float): 지수 (필수)
    
    반환값:
        str: base^exponent의 결과
    """
    try:
        result = math.pow(base, exponent)
        return f"{base}^{exponent} = {result}"
    except Exception as e:
        return f"계산 오류: {str(e)}"

@mcp.tool()
def square_root(number: float) -> str:
    """
    제곱근을 계산하는 도구
    
    매개변수:
        number (float): 제곱근을 구할 숫자 (필수, 0 이상)
    
    반환값:
        str: √number의 결과 또는 오류 메시지
    """
    if number < 0:
        return "오류: 음수의 제곱근은 계산할 수 없습니다."
    result = math.sqrt(number)
    return f"√{number} = {result}"

# ===== 유틸리티 도구들 =====

@mcp.tool()
def random_number(min_val: int = 1, max_val: int = 100) -> str:
    """
    지정된 범위에서 임의의 숫자를 생성하는 도구
    
    매개변수:
        min_val (int): 최솟값 (기본값: 1)
        max_val (int): 최댓값 (기본값: 100)
    
    반환값:
        str: 생성된 임의 숫자와 범위 정보
    """
    if min_val > max_val:
        return "오류: 최솟값이 최댓값보다 클 수 없습니다."
    
    result = random.randint(min_val, max_val)
    return f"{min_val}부터 {max_val} 사이의 임의 숫자: {result}"

@mcp.tool()
def flip_coin() -> str:
    """
    동전 던지기를 시뮬레이션하는 도구
    
    매개변수: 없음
    
    반환값:
        str: "앞면" 또는 "뒷면" 결과
    """
    result = random.choice(["앞면", "뒷면"])
    return f"동전 던지기 결과: {result}"

@mcp.tool()
def roll_dice(sides: int = 6, count: int = 1) -> str:
    """
    주사위 굴리기를 시뮬레이션하는 도구
    
    매개변수:
        sides (int): 주사위 면의 수 (기본값: 6)
        count (int): 굴릴 주사위 개수 (기본값: 1)
    
    반환값:
        str: 주사위 굴리기 결과들과 총합
    """
    if sides < 2:
        return "오류: 주사위는 최소 2면이어야 합니다."
    if count < 1:
        return "오류: 주사위 개수는 최소 1개여야 합니다."
    if count > 10:
        return "오류: 주사위는 최대 10개까지만 굴릴 수 있습니다."
    
    results = [random.randint(1, sides) for _ in range(count)]
    total = sum(results)
    
    if count == 1:
        return f"{sides}면 주사위 결과: {results[0]}"
    else:
        return f"{sides}면 주사위 {count}개 결과: {results} (총합: {total})"

# ===== 텍스트 처리 도구들 =====

@mcp.tool()
def count_words(text: str) -> str:
    """
    텍스트의 단어 수를 세는 도구
    
    매개변수:
        text (str): 분석할 텍스트 (필수)
    
    반환값:
        str: 단어 수, 문자 수, 줄 수 정보
    """
    if not text.strip():
        return "빈 텍스트입니다."
    
    words = len(text.split())
    chars = len(text)
    chars_no_spaces = len(text.replace(" ", ""))
    lines = len(text.split("\n"))
    
    return f"""텍스트 분석 결과:
- 단어 수: {words}개
- 전체 문자 수: {chars}개
- 공백 제외 문자 수: {chars_no_spaces}개  
- 줄 수: {lines}개"""

@mcp.tool()
def reverse_text(text: str) -> str:
    """
    텍스트를 뒤집는 도구
    
    매개변수:
        text (str): 뒤집을 텍스트 (필수)
    
    반환값:
        str: 뒤집어진 텍스트
    """
    if not text:
        return "빈 텍스트입니다."
    
    reversed_text = text[::-1]
    return f"원본: {text}\n뒤집은 결과: {reversed_text}"

@mcp.tool()
def to_upper_lower(text: str, mode: str = "upper") -> str:
    """
    텍스트를 대문자 또는 소문자로 변환하는 도구
    
    매개변수:
        text (str): 변환할 텍스트 (필수)
        mode (str): "upper" 또는 "lower" (기본값: "upper")
    
    반환값:
        str: 변환된 텍스트
    """
    if not text:
        return "빈 텍스트입니다."
    
    if mode.lower() == "upper":
        result = text.upper()
        return f"대문자 변환: {result}"
    elif mode.lower() == "lower":
        result = text.lower()
        return f"소문자 변환: {result}"
    else:
        return "오류: mode는 'upper' 또는 'lower'여야 합니다."

# ===== 정보 조회 도구들 =====

@mcp.tool()
def system_info() -> str:
    """
    시스템 정보를 조회하는 도구
    
    매개변수: 없음
    
    반환값:
        str: 현재 작업 디렉토리와 기본 시스템 정보
    """
    cwd = os.getcwd()
    return f"""시스템 정보:
- 현재 작업 디렉토리: {cwd}
- 운영체제: {os.name}
- 서버 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

@mcp.tool()
def calculate_age(birth_year: int) -> str:
    """
    출생 연도로부터 나이를 계산하는 도구
    
    매개변수:
        birth_year (int): 출생 연도 (필수)
    
    반환값:
        str: 계산된 나이 정보
    """
    current_year = datetime.now().year
    
    if birth_year > current_year:
        return "오류: 출생 연도가 현재 연도보다 클 수 없습니다."
    if birth_year < 1900:
        return "오류: 1900년 이후 출생 연도만 지원합니다."
    
    age = current_year - birth_year
    return f"{birth_year}년생의 현재 나이: 만 {age}세 (또는 만 {age-1}세)"

# ===== 서버 실행 =====
if __name__ == "__main__":
    # 표준 입출력(stdin/stdout)을 통해 MCP 프로토콜 서버 시작
    # 클라이언트와의 JSON-RPC 통신을 처리함
    print("MultiToolServer 시작됨 - 사용 가능한 도구들:")
    print("- 인사말: hello")
    print("- 계산기: add, multiply, subtract, divide, power, square_root") 
    print("- 시간: now")
    print("- 랜덤: random_number, flip_coin, roll_dice")
    print("- 텍스트: count_words, reverse_text, to_upper_lower")
    print("- 정보: system_info, calculate_age")
    mcp.run()
