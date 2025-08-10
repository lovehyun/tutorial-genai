import sys
import json
from mcp.server.fastmcp import FastMCP

# 최소 확장 MCP 서버 생성
mcp = FastMCP("MinimalServer")

# === 도구 1개 ===
@mcp.tool()
def hello(name: str = "World") -> str:
    """간단한 인사말을 반환합니다."""
    print(f"[SERVER] hello 함수 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}!"

# === 리소스 1개 ===
@mcp.resource("data://info.json")
def get_info() -> str:
    """서버 정보를 반환합니다."""
    print(f"[SERVER] get_info 리소스 요청됨", file=sys.stderr)
    info = {
        "server_name": "MinimalServer",
        "message": "이것은 테스트 리소스입니다"
    }
    return json.dumps(info, indent=2, ensure_ascii=False)

# === 프롬프트 1개 ===
@mcp.prompt()
def greeting(name: str = "사용자") -> str:
    """간단한 인사 프롬프트입니다."""
    print(f"[SERVER] greeting 프롬프트 호출됨: name={name}", file=sys.stderr)
    
    prompt = f"안녕하세요 {name}님! 도구, 리소스, 프롬프트를 각각 하나씩 가진 서버입니다."
    
    return prompt

if __name__ == "__main__":
    print("[SERVER] 최소 확장 서버 시작됨", file=sys.stderr)
    print("[SERVER] 제공 기능: 도구 1개, 리소스 1개, 프롬프트 1개", file=sys.stderr)
    mcp.run()
