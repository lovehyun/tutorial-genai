# client2.py — 파일시스템 MCP '고급' 클라이언트 (9툴, server2.py)
# client.py(간단, 4툴)의 확장판: 쓰기/생성/삭제/검색/정보까지. 자동 데모 + 대화형 셸.
#
# ── 연동 방식 ────────────────────────────────────────────────
#   server/server2.py 를 띄우고(도구 9개), 한 세션 안에서 call(session, name, **args) 로 호출.
#   각 도구는 dict(JSON)를 반환 → 그대로 출력. (client.py 의 4툴과 달리 write/delete/search 까지)
#   ※ 반드시 1.filesystem 폴더에서 실행:  python client/client2.py

import asyncio
import json
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command="python", args=["server/server2.py"])


@asynccontextmanager
async def open_session():
    """서버를 띄우고 초기화된 세션을 넘긴다 (한 task scope 안에서 안전하게 유지)."""
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call(session, name, **args):
    """도구 호출 → 결과 반환.
    dict 반환 도구는 content[0].text(JSON)로, list 반환 도구(list_files/search_files)는
    structuredContent 로 오므로 둘 다 방어적으로 처리한다."""
    r = await session.call_tool(name, args)
    if r.content and getattr(r.content[0], "text", ""):
        return r.content[0].text
    return getattr(r, "structuredContent", None) or "(결과 없음)"


async def demo():
    async with open_session() as s:
        print("도구:", [t.name for t in (await s.list_tools()).tools])
        print("쓰기 :", await call(s, "write_file", file_path="demo.txt", content="hello mcp", overwrite=True))
        print("읽기 :", await call(s, "read_file", file_path="demo.txt"))
        print("정보 :", await call(s, "get_file_info", file_path="demo.txt"))
        print("삭제 :", await call(s, "delete_file", file_path="demo.txt"))
        # (list_files / search_files 는 server2 가 list 를 반환 → 대화형 ls/find 에서 시도)


# 대화형 명령 → (도구, 인자) 매핑
CMDS = {
    "ls":    lambda a: ("list_files", {"directory": a[0] if a else "."}),
    "cat":   lambda a: ("read_file", {"file_path": a[0]}),
    "write": lambda a: ("write_file", {"file_path": a[0], "content": " ".join(a[1:]), "overwrite": True}),
    "mkdir": lambda a: ("create_directory", {"directory_path": a[0]}),
    "rm":    lambda a: ("delete_file", {"file_path": a[0]}),
    "find":  lambda a: ("search_files", {"pattern": a[0]}),
    "info":  lambda a: ("get_file_info", {"file_path": a[0]}),
}


async def interactive():
    async with open_session() as s:
        print("명령: ls / cat <f> / write <f> <내용> / mkdir <d> / rm <f> / find <pat> / info <f> / quit")
        loop = asyncio.get_event_loop()
        while True:
            parts = (await loop.run_in_executor(None, input, "\nfs> ")).split()
            if not parts:
                continue
            if parts[0] == "quit":
                break
            spec = CMDS.get(parts[0])
            if not spec:
                print("알 수 없는 명령")
                continue
            name, args = spec(parts[1:])
            print(await call(s, name, **args))


if __name__ == "__main__":
    print("1. 자동 데모   2. 대화형 셸")
    asyncio.run(interactive() if input("선택 (1/2): ").strip() == "2" else demo())

# ── 실행 결과 (예, 자동 데모) ───────────────────────────────
#   도구: ['list_files', 'read_file', 'write_file', 'create_directory', 'delete_file',
#          'copy_file', 'move_file', 'search_files', 'get_file_info']
#   쓰기 : {'message': '...', 'size': 9, ...}
#   읽기 : {'content': 'hello mcp', ...}
#   삭제 : {'message': 'demo.txt 삭제 완료'}
