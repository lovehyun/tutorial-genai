"""
MCP 3단계: 내 서버를 확장한다 — 도구 여러 개 + resource.
이 예제: add 외에 도구 2개를 더 추가하고, '리소스(resource)' 개념을 소개한다.

도구(tool) vs 리소스(resource):
  - tool     : 모델이 '실행' 하는 동작 (함수 호출). 부작용/계산이 있을 수 있다.
  - resource : 모델이 '읽는' 데이터 (URI 로 식별). 파일·설정·문서 같은 읽기 전용 컨텍스트.

준비:
  pip install mcp

실행:
  - 단독 실행하면 stdio 서버로 대기한다(정상).
  - 4.langchain/1.quickstart/1.agent 가 이 서버를 자식 프로세스로 띄워 도구를 사용한다.
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("toolbox")


# ─── 도구 여러 개 ──────────────────────────────────────────
@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 더한다."""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """두 정수 a 와 b 를 곱한다."""
    return a * b


@mcp.tool()
def word_count(text: str) -> int:
    """주어진 문자열의 단어 개수를 센다."""
    return len(text.split())


# ─── 리소스 — 읽기 전용 데이터(URI 로 식별) ──────────────────
@mcp.resource("info://server")
def server_info() -> str:
    """이 서버가 무엇인지 알려주는 소개 텍스트."""
    return "demo toolbox MCP 서버 v1 — add / multiply / word_count 도구 제공"


if __name__ == "__main__":
    mcp.run()

# 정리:
#   - 함수만 추가하면 도구가 늘어난다(서버 코드만 고치면 됨).
#   - 이 서버를 쓰는 클라이언트/에이전트 코드는 바뀌지 않는다 → 도구와 사용처의 분리.
