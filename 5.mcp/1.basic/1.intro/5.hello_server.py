# 도구 3개짜리 MCP 서버 — 다음 예제(2.hello_client_llm.py)에서 LLM이 이 중 뭘 쓸지 스스로 고른다.
# pip install "mcp[cli]"

from datetime import datetime

from mcp.server.fastmcp import FastMCP

# FastMCP 객체 생성 — 3.hello_server.py 와 같은 이름의 서버, 도구만 늘렸다.
mcp = FastMCP("HelloWorld")


@mcp.tool()
def hello(name: str = "World") -> str:
    """이름을 넣어 인사말을 돌려준다."""
    return f"Hello, {name}!"


@mcp.tool()
def get_date() -> str:
    """오늘 날짜를 돌려준다."""
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_time() -> str:
    """지금 시각을 돌려준다."""
    return datetime.now().strftime("%H:%M:%S")


# MCP 서버 실행 — stdio 로 도구 3개(hello, get_date, get_time)를 노출한다.
# 날씨 도구는 일부러 안 넣었다 — 6.hello_client_llm.py 에서 "도구가 없는 질문"을 물어봤을 때
# LLM 이 있는 도구 중 아무거나 억지로 부르지 않고 "그런 도구가 없다"고 답하는지 확인해본다.
if __name__ == "__main__":
    mcp.run()
