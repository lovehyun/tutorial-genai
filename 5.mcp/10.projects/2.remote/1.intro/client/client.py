# client.py — 원격(HTTP) MCP 서버에 붙는 클라이언트 (streamable-http)
#
# ── 연동 방식 ────────────────────────────────────────────────
#   stdio 와 달리 서버를 직접 안 띄운다 — 이미 떠 있는 원격 서버에 URL 로 접속.
#     streamablehttp_client(url) → ClientSession → initialize → list_tools → call_tool
#   흐름은 stdio 와 동일하고 '접속부'만 다르다.
#   ※ 먼저 다른 터미널에서 서버 실행:  python server/server.py   (http://localhost:8000/mcp)

import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()
URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")


def text(result):
    return result.content[0].text if result.content else str(result)


async def auto(session):
    print(f"=== 자동 테스트 ({URL}) ===")
    cases = [("hello", {"name": "MCP User"}), ("add", {"a": 15, "b": 25}),
             ("multiply", {"a": 7, "b": 8}), ("current_time", {}),
             ("weather", {"city": "Seoul"}), ("echo", {"message": "Hello MCP"})]
    for name, args in cases:
        print(f"  {name}({args}) → {text(await session.call_tool(name, args))}")


# 대화형 명령 → (도구, 인자)
CMDS = {
    "hello":    lambda a: ("hello", {"name": a[0] if a else "World"}),
    "add":      lambda a: ("add", {"a": float(a[0]), "b": float(a[1])}),
    "multiply": lambda a: ("multiply", {"a": float(a[0]), "b": float(a[1])}),
    "time":     lambda a: ("current_time", {}),
    "weather":  lambda a: ("weather", {"city": a[0] if a else "Seoul"}),
    "echo":     lambda a: ("echo", {"message": " ".join(a) or "Hello!"}),
}


async def interactive(session):
    print("명령: hello <name> / add <a> <b> / multiply <a> <b> / time / weather <city> / echo <msg> / quit")
    loop = asyncio.get_event_loop()
    while True:
        try:
            parts = (await loop.run_in_executor(None, input, "\n명령> ")).split()
        except EOFError:
            break
        if not parts or parts[0] == "quit":
            break
        spec = CMDS.get(parts[0])
        if not spec:
            print("알 수 없는 명령")
            continue
        name, args = spec(parts[1:])
        print("→", text(await session.call_tool(name, args)))


async def main():
    async with streamablehttp_client(URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("도구:", [t.name for t in (await session.list_tools()).tools])
            mode = input("1=자동  2=대화형 (기본 1): ").strip()
            await (interactive(session) if mode == "2" else auto(session))


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'multiply', 'current_time', 'weather', 'get_server_info', 'echo']
#   hello({'name': 'MCP User'}) → Hello, MCP User! (from remote server)
#   add({'a': 15, 'b': 25}) → 15.0 + 25.0 = 40.0
