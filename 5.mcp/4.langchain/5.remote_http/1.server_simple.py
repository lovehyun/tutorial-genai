# 1.server_simple.py — HTTP(streamable-http) 로 뜨는 MCP 서버
#
# ── 이 파일의 핵심: 서버에는 LangChain 이 없다 ────────────────────
#   MCP 서버의 책임은 "도구 목록/스키마를 노출하고, 호출되면 실행해 결과를 돌려주는 것" 뿐이다.
#   '어떤 도구를 쓸지 LLM 이 고르게 하는' 일은 전부 클라이언트(에이전트) 쪽 몫이므로
#   서버 코드에 langchain import 는 단 한 줄도 필요 없다.
#   → 그래서 이 서버는 LangChain 에이전트뿐 아니라 Claude Desktop / Codex /
#     순수 ClientSession(1.basic) 어디에 붙여도 그대로 동작한다. (프레임워크 중립)
#
# ── stdio 서버(2~4.langchain 폴더) 와의 차이 ─────────────────────
#   stdio : 클라이언트가 서버를 '자식 프로세스' 로 띄운다 → 서버는 내 PC 안에서만 산다
#   http  : 서버를 먼저 띄워두고, 클라이언트가 URL 로 '접속' 한다 → 원격/공용 가능
#   바뀌는 코드는 mcp.run() 한 줄뿐이고, 도구 정의는 완전히 동일하다.
#
# 실행:  python 1.server_simple.py     → http://127.0.0.1:8000/mcp

from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ※ host/port 는 run() 이 아니라 FastMCP 생성자에서 지정한다 (mcp SDK 규칙).
#    run() 은 transport 만 받는다.
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
    #    둘이 달라서 자주 틀린다 → 2.client_agent.py 주석 참고.
    mcp.run(transport="streamable-http")
