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
# Windows: %APPDATA%\Claude\claude_desktop_config.json
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

from mcp.server.fastmcp import FastMCP
import logging

mcp = FastMCP("hello")  # 서버 이름

@mcp.tool()
async def hello(name: str) -> str:
    """간단한 인사말을 돌려줍니다."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # stdout에 print() 금지! 로거는 stderr로 흘러가도록 설정
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")
