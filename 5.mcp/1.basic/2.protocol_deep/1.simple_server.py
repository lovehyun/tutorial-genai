import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SimpleServer")

@mcp.tool()
def hello(name: str = "World") -> str:
    # ⚠️ 로그는 반드시 stderr 로! stdout 은 JSON-RPC 채널이라 print() 하면 채널이 오염된다
    #    (특히 Windows 에선 한글이 cp949 로 나가 클라이언트의 UTF-8 디코딩이 깨진다)
    # print(f"[SERVER] hello 함수 호출됨: name={name}")
    print(f"[SERVER] hello 함수 호출됨: name={name}", file=sys.stderr)
    return f"Hello, {name}!"


if __name__ == "__main__":
    print("[SERVER] 서버 시작됨", file=sys.stderr)   # stdout 금지 → stderr 로만
    mcp.run()


# stdout 으로 출력시 발생하는 오류
#
# python 2.simple_client.py
# [CLIENT] 도구: ['hello']
# Failed to parse JSONRPC message from server
# Traceback (most recent call last):
#   File "C:\devs\anaconda3\envs\py312_gpt\Lib\site-packages\mcp\client\stdio\__init__.py", line 155, in stdout_reader
#     message = types.JSONRPCMessage.model_validate_json(line)
#               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\devs\anaconda3\envs\py312_gpt\Lib\site-packages\pydantic\main.py", line 782, in model_validate_json
#     return cls.__pydantic_validator__.validate_json(
#            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# pydantic_core._pydantic_core.ValidationError: 1 validation error for JSONRPCMessage
