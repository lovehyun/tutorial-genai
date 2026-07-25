"""
VSCode 연동용 MCP 서버 — 내 도구를 VSCode Copilot Agent Mode 에서 쓰게 한다.
이 예제: 개발에 쓸만한 작은 도구 3개 + 서버 정보 resource 를 가진 FastMCP 서버.

핵심:
  - 1.common 에서 배운 FastMCP 서버와 똑같다 — 달라지는 건 '클라이언트가 VSCode' 라는 점뿐.
  - 같은 서버를 .vscode/mcp.json 으로 등록하면 Copilot 채팅(Agent Mode)이 이 도구들을 호출한다.

준비:
  pip install mcp

단독 테스트(선택):
  pip install "mcp[cli]"
  mcp dev server.py          # Inspector 로 도구 확인
  # 또는 1.common/1.intro/4.hello_client.py 스타일로 직접 호출

VSCode 등록:
  같은 폴더의 .vscode/mcp.json 참고 → README.md 워크스루대로 진행.
"""

import re
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("dev-helper")


@mcp.tool()
def add(a: int, b: int) -> int:
    """두 정수 a 와 b 를 더한다."""
    return a + b


@mcp.tool()
def word_count(text: str) -> int:
    """주어진 문자열의 단어 개수를 센다 (공백 기준)."""
    return len(text.split())


@mcp.tool()
def to_snake_case(name: str) -> str:
    """camelCase / PascalCase / 공백 이름을 snake_case 로 변환한다.
    예) 'myVariableName' → 'my_variable_name', 'User Profile' → 'user_profile'."""
    s = re.sub(r"[\s\-]+", "_", name.strip())          # 공백/하이픈 → _
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", s)       # camelCase 경계에 _
    return s.lower()


@mcp.resource("info://server")
def server_info() -> str:
    """이 서버 소개."""
    return "dev-helper MCP 서버 — add / word_count / to_snake_case 도구 제공 (VSCode 연동 데모)"


if __name__ == "__main__":
    mcp.run()   # 기본 stdio — VSCode 가 자식 프로세스로 띄워 통신한다
