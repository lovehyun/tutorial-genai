"""
인증된 원격 MCP 클라이언트 — Bearer 토큰을 헤더에 실어 접속한다.

핵심은 딱 한 줄: streamablehttp_client(url, headers={"Authorization": f"Bearer {token}"}).
나머지(initialize / list_tools / call_tool)는 1.intro 와 완전히 동일하다.

이 스크립트는 두 번 접속을 시도한다:
  1) 토큰 '없이'  → 401 로 거부되는지 확인
  2) 올바른 토큰  → 정상 동작

준비:  pip install mcp python-dotenv
실행:  (터미널1) python server.py   후   (터미널2) python client.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()
URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
TOKEN = os.getenv("MCP_API_TOKEN", "secret-token-123")


def _root_cause(e: BaseException) -> BaseException:
    """streamable-http 는 오류를 TaskGroup ExceptionGroup 으로 감싼다 → 가장 안쪽 원인을 꺼낸다."""
    while isinstance(e, BaseExceptionGroup) and e.exceptions:
        e = e.exceptions[0]
    return e


async def try_connect(headers: dict | None, label: str):
    print(f"\n=== {label} ===")
    try:
        async with streamablehttp_client(URL, headers=headers) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = [t.name for t in (await session.list_tools()).tools]
                print("  접속 성공. 도구:", tools)
                r = await session.call_tool("hello", {"name": "인증사용자"})
                print("  hello →", r.content[0].text)
    except Exception as e:
        # 401 이면 여기서 예외로 잡힌다 (ExceptionGroup 안쪽에 실제 원인이 있다)
        cause = _root_cause(e)
        print(f"  거부/실패: {type(cause).__name__}: {cause}")


async def main():
    # 1) 토큰 없이 → 거부되어야 정상
    await try_connect(None, "토큰 없이 접속 (거부 예상)")

    # 2) 올바른 토큰 → 통과
    await try_connect({"Authorization": f"Bearer {TOKEN}"}, "Bearer 토큰으로 접속 (성공 예상)")


if __name__ == "__main__":
    asyncio.run(main())

# 정리:
#   - stdio→HTTP 때 접속부 한 줄만 바뀌었듯, 인증도 'headers 한 줄' 이 전부다.
#   - 토큰을 코드에 박지 말고 .env / 환경변수 / 시크릿 매니저에서 읽어라.
