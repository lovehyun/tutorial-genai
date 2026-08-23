from mcp.server.fastmcp import FastMCP
from datetime import datetime

# 2.openai/1.agent_tool/server.py 와 완전히 같은 도구 3개 — 일부러 똑같이 만들었다.
# "서버는 벤더를 모른다"는 걸 보여주려면, 진짜로 같은 서버를 OpenAI/Claude 양쪽에 붙여봐야 한다.

mcp = FastMCP("MultiToolServer")


@mcp.tool()
def hello(name: str = "World") -> str:
    """사용자에게 개인화된 인사말을 생성하는 도구."""
    return f"Hello, {name}!"


@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수의 덧셈을 수행하는 계산기 도구."""
    return a + b


@mcp.tool()
def now() -> str:
    """현재 시간을 한국어로 포맷하여 반환하는 도구."""
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")


if __name__ == "__main__":
    mcp.run()
