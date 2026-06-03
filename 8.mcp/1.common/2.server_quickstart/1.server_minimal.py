"""
MCP 1단계: 내 MCP 서버를 직접 만든다 (가장 기본).
이 예제: FastMCP 로 도구 1개(add)를 가진 MCP 서버를 작성한다.

핵심:
  - MCP '서버' = 도구를 제공하는 독립 프로세스. LLM 도 LangChain 도 아직 없다.
  - @mcp.tool() 로 등록한 함수가 곧 MCP 도구가 된다.
    함수 시그니처(타입)와 docstring 이 그대로 도구 명세(LLM 이 읽는 설명)가 된다.
  - mcp.run() 은 기본으로 stdio(표준 입출력) 로 통신하는 서버를 띄운다.

준비:
  pip install mcp

실행 방법(2가지):
  1) 직접 실행 — 서버가 stdio 로 떠서 입력을 기다린다(혼자 실행하면 멈춘 듯 보임. 정상).
       python 1.server_minimal.py
     → 이 서버는 '클라이언트' 가 붙어야 의미가 있다. 클라이언트는 2.client_raw.py 에서.
  2) 2.client_raw.py 가 이 파일을 자식 프로세스로 띄워 자동으로 호출한다(권장).

다음 단계:
  - 2.client_raw            : 이 서버에 직접 붙어 도구를 호출(프로토콜을 눈으로 본다)
  - 3.server_tools_resource : 도구 여러 개 + resource 로 확장
  - ../../4.langchain/      : 이 서버를 LangChain 에이전트가 자동으로 골라 쓰게 만든다
"""

from mcp.server.fastmcp import FastMCP

# 서버 이름 — 클라이언트 쪽에서 식별용으로 보인다.
mcp = FastMCP("calculator")


@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 더한 값을 돌려준다."""
    return a + b


if __name__ == "__main__":
    # transport 기본값은 "stdio". (HTTP 로 띄우려면 mcp.run(transport="streamable-http"))
    mcp.run()
