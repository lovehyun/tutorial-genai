# server.py — 웹 챗봇 데모용 MCP 서버 (재미있고 유용한 도구 모음)
# 이 서버를 app.py(웹)가 자식 프로세스로 띄우고, 에이전트가 도구를 자동 호출한다.

from datetime import datetime
import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("chatbot-tools")


@mcp.tool()
def calculator(expression: str) -> str:
    """수학 식을 계산한다. 예: '12 * 7 + 3'"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"계산 오류: {e}"


@mcp.tool()
def now() -> str:
    """현재 날짜와 시간을 알려준다."""
    return datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")


@mcp.tool()
def roll_dice(sides: int = 6) -> str:
    """주사위를 굴린다 (기본 6면)."""
    return f"🎲 {random.randint(1, sides)} (1~{sides})"


@mcp.tool()
def weather(city: str) -> str:
    """도시의 날씨를 알려준다 (데모용 가짜 데이터)."""
    data = {"서울": "맑음 22도", "부산": "흐림 25도", "제주": "비 19도"}
    return data.get(city, f"{city}: 날씨 정보 없음")


if __name__ == "__main__":
    mcp.run()   # stdio
