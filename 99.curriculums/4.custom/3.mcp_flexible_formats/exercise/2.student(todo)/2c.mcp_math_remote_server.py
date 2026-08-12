"""
mcp-math 원격 서버 — 2a.mcp_math_local_server.py 와 같은 개념을, stdio 대신 HTTP 로 노출한다.
바뀌는 코드는 mcp.run() 딱 한 줄뿐이고, 도구 정의는 완전히 동일하다 — 그 한 줄을 직접 채워보자.

실행:  python 2c.mcp_math_remote_server.py     → http://127.0.0.1:8000/mcp
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RemoteToolbox", host="127.0.0.1", port=8000)


@mcp.tool()
def hello(name: str = "World") -> str:
    """사용자에게 개인화된 인사말을 생성한다."""
    return f"Hello, {name}!"


@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수를 더한다."""
    return a + b


@mcp.tool()
def word_count(text: str) -> int:
    """주어진 문자열의 단어 개수를 센다."""
    return len(text.split())


@mcp.tool()
def now() -> str:
    """현재 서버 시각을 조회한다."""
    return datetime.now().strftime("지금 시간은 %Y-%m-%d %H:%M:%S 입니다.")


if __name__ == "__main__":
    print("=" * 60)
    print("RemoteToolbox MCP 서버 (streamable-http)")
    print("  주소: http://127.0.0.1:8000/mcp")
    print("  종료: Ctrl+C")
    print("=" * 60)

    # TODO: mcp.run() 을 stdio 가 아니라 HTTP(streamable-http) 로 뜨게 바꾸세요.
    #   힌트 — mcp.run(transport="???")
    #   ⚠️ 리터럴 주의: 여기(서버)는 하이픈("streamable-http")을 쓴다.
    #     클라이언트(langchain-mcp-adapters) 설정에서는 언더스코어("streamable_http")를 쓴다 — 서로 다르다.
    mcp.run()  # ← transport 인자를 채우세요
