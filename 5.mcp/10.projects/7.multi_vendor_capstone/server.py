# pip install mcp
#
# 이 캡스톤의 서버는 특별할 게 없다 — 그게 핵심이다. 도구 2개짜리 평범한 MCP 서버 하나를
# 만들어두면, 1.client_openai.py / 2.client_anthropic.py / 3.client_langchain.py 가
# **이 서버를 고치지 않고 그대로** 각자 다른 벤더로 붙는다. "서버 한 번, 클라이언트는 벤더 수만큼"
# 이라는 MCP의 핵심 가치를 세 벤더 클라이언트가 나란히 붙는 걸로 직접 증명한다.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("capstone-toolbox")


@mcp.tool()
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 반환한다(데모용 고정 데이터)."""
    fake_weather = {
        "서울": "맑음, 22도",
        "부산": "흐림, 19도",
        "제주": "비, 17도",
    }
    return fake_weather.get(city, f"{city}: 데이터 없음(맑음, 20도로 가정)")


@mcp.tool()
def calculate(expression: str) -> str:
    """숫자와 +-*/() 로만 이루어진 산술식을 계산한다."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "허용되지 않은 문자가 포함되어 있습니다(숫자와 +-*/() 만 가능)."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 실패: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
