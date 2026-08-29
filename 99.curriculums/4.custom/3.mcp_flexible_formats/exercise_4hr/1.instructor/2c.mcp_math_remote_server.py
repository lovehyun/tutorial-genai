"""
mcp-math 원격 서버 — 2a.mcp_math_local_server.py 와 같은 개념을, stdio 대신 HTTP 로 노출한다.
바뀌는 코드는 mcp.run() 한 줄뿐이고, 도구 정의는 완전히 동일하다.

실행:  python 2c.mcp_math_remote_server.py     → http://127.0.0.1:8000/mcp

원본: 5.mcp/4.langchain/5.remote_http/1.server_simple.py
"""

from datetime import datetime

from mcp.server.fastmcp import FastMCP

# host/port 는 run() 이 아니라 FastMCP 생성자에서 지정한다 (mcp SDK 규칙).
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

    # ⚠️ 리터럴 주의: 여기선 하이픈("streamable-http") 이다.
    #    클라이언트(langchain-mcp-adapters) 설정에서는 언더스코어("streamable_http") 를 쓴다.
    mcp.run(transport="streamable-http")


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# ============================================================
# RemoteToolbox MCP 서버 (streamable-http)
#   주소: http://127.0.0.1:8000/mcp
#   종료: Ctrl+C
# ============================================================
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# StreamableHTTP session manager started
# (이후 클라이언트가 접속하면 "Processing request of type ..." 로그가 이어진다)
# 클라이언트 쪽 결과는 2d.mcp_math_remote_client.py 하단 참고.
