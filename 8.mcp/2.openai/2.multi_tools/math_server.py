import sys
from mcp.server.fastmcp import FastMCP

# 수학 관련 기능을 제공하는 서버
mcp = FastMCP("MathServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    """친근한 인사말을 생성합니다."""
    print(f"[MATH_SERVER] hello 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}! 저는 수학 서버입니다."

@mcp.tool()
def add(a: float, b: float) -> str:
    """두 숫자를 더합니다."""
    print(f"[MATH_SERVER] add 호출됨: {a} + {b}", file=sys.stderr)
    result = a + b
    return f"{a} + {b} = {result}"

if __name__ == "__main__":
    print("[MATH_SERVER] 수학 서버 시작됨", file=sys.stderr)
    print("[MATH_SERVER] 제공 기능: hello, add", file=sys.stderr)
    mcp.run()

# 1. 초기화
# {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cli-test","version":"0.1.0"}}}
# 2. initialized 알림(중요, id 없음)
# {"jsonrpc":"2.0","method":"notifications/initialized"}
# 3. 도구 목록 조회
# {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
# 4. hello 호출
# {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"hello","arguments":{"name":"Alice"}}}
# 5. add 호출
# {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add","arguments":{"a":5,"b":7}}}

# python math_server.py <<'EOF'
# {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cli-test","version":"0.1.0"}}}
# {"jsonrpc":"2.0","method":"notifications/initialized"}
# {"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
# {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"hello","arguments":{"name":"Alice"}}}
# {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"add","arguments":{"a":5,"b":7}}}
# EOF
