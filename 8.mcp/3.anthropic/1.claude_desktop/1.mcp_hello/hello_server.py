# 1. 가상 환경 생성
# uv venv

# 2. 활성화
# macOS/Linux
# source .venv/bin/activate
# Windows (PowerShell)
# . .venv\Scripts\Activate.ps1

# 3. MCP Python SDK(+CLI) 설치
# uv pip install "mcp[cli]"

# 4. 개발 및 테스트
# uv run mcp dev hello_server.py
# uv run hello_server.py
 
# 5.1 설정 파일 위치
# Windows: %APPDATA%\Claude\claude_desktop_config.json  (APPDATA = C:\Users\loveh\AppData\Roaming)
# MacOS: ~/Library/Application Support/Claude/claude_desktop_config.json

# 5.2 로그 파일 위치
# Windows: %APPDATA%\Claude\logs  (APPDATA = C:\Users\loveh\AppData\Roaming)
# MacOS: ~/Library/Logs/Claude

import logging
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello")  # 서버 이름

@mcp.tool()
async def hello(name: str) -> str:
    """간단한 인사말을 돌려줍니다."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # stdout에 print() 금지! 로거는 기본적으로 stderr로 흘러가도록 설정
    logging.basicConfig(level=logging.INFO)
    logging.info("MCP 서버 'hello'를 stdio 전송 방식으로 시작합니다...")
    mcp.run(transport="stdio")


# {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{"elicitation":{}},"clientInfo":{"name":"demo-client","version":"1.0.0"}}}
# {"jsonrpc":"2.0","method":"notifications/initialized"}
# {"jsonrpc":"2.0","id":2,"method":"tools/list"}
# {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"hello","arguments":{"name":"shpark"}}}
