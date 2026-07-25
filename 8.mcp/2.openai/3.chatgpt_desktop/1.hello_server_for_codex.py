"""
hello_server.py — Codex CLI에서 사용하는 로컬 MCP 서버

실행 구조:
    Codex CLI
        ↓ STDIO
    FastMCP 서버
        ↓
    hello 도구 호출

설치:
    uv venv
    uv pip install "mcp[cli]"

직접 테스트:
    uv run mcp dev hello_server.py
    uv run hello_server.py

Codex CLI 설치:
    npm install -g @openai/codex
    codex --version

Codex 등록:
    codex mcp add hello -- uv run hello_server.py

Codex 수동등록:
    Windows:
        %USERPROFILE%\.codex\config.toml
        예)
        C:\Users\loveh\.codex\config.toml

---
[mcp_servers.hello]
command = "uv"
args = ["run", "hello_server.py"]
cwd = "C:\\src\\mcp"
enabled = true
---

    MAC/Linux
        ~/.codex/config.toml
---
[mcp_servers.hello]
command = "uv"
args = ["run", "hello_server.py"]
cwd = "/Users/shpark/src/mcp"
enabled = true
---
        
등록 확인:
    codex mcp list

Codex 실행:
    codex

Codex 안에서:
    /mcp

질문 예:
    "hello 도구를 사용해서 Park에게 인사해줘."
    "반드시 hello MCP 도구를 사용해서 Park에게 인사해줘."
"""

import logging

from mcp.server.fastmcp import FastMCP


# Codex에 표시되는 MCP 서버 이름
mcp = FastMCP("hello")


@mcp.tool()
async def hello(name: str) -> str:
    """
    전달받은 이름을 사용해 영어 인사말을 반환합니다.

    Args:
        name: 인사할 사람의 이름

    Returns:
        인사말 문자열
    """
    return f"Hello, {name}!"


if __name__ == "__main__":
    # STDIO 기반 MCP 서버에서는 stdout에 print()를 사용하면 안 됩니다.
    # stdout은 JSON-RPC 메시지 전송에 사용되기 때문입니다.
    logging.basicConfig(level=logging.INFO)

    logging.info(
        "Codex용 MCP 서버 'hello'를 STDIO 전송 방식으로 시작합니다."
    )

    mcp.run(transport="stdio")
