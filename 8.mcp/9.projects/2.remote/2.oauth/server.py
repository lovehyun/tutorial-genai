"""
원격 MCP 서버 + 인증(Bearer 토큰) — 2.remote/1.intro 의 '무인증' 버전에 보호막을 씌운다.

1.intro 서버는 URL 만 알면 누구나 붙는다. 실전 원격 서버는 그럴 수 없다.
여기서는 streamable-http 앱 앞에 **Bearer 토큰 검사 미들웨어**를 끼워,
올바른 토큰을 실은 요청만 /mcp 로 통과시킨다.

    클라이언트 ──[Authorization: Bearer <TOKEN>]──▶  미들웨어 검사 ──▶ MCP 서버
                                     토큰 없음/틀림 ──▶ 401 Unauthorized

⚠️ 범위 안내:
   이건 '정적 토큰' 최소 예제다. 실제 프로덕션의 완전한 MCP 인증은
   OAuth 2.1(Protected Resource Metadata, 동적 토큰 발급/검증)을 쓴다 — README 링크 참고.
   여기서는 "인증이 왜/어디에 끼는지" 를 먼저 눈으로 익히는 게 목적.

준비:  pip install mcp uvicorn
실행:  python server.py            # http://127.0.0.1:8000/mcp  (Bearer 필요)
"""

import os

import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server.fastmcp import FastMCP

# 실제로는 환경변수/시크릿 매니저에서 읽는다. 데모라 기본값을 둔다.
API_TOKEN = os.getenv("MCP_API_TOKEN", "secret-token-123")

mcp = FastMCP("SecureRemoteServer")


@mcp.tool()
def hello(name: str = "World") -> str:
    """인사말을 생성합니다."""
    return f"Hello, {name}! (from SECURE remote server)"


@mcp.tool()
def whoami() -> str:
    """인증을 통과한 호출자에게 보이는 서버 메시지."""
    return "인증된 요청입니다 (OK)"


# ── Bearer 토큰 검사 미들웨어 ────────────────────────────────────────
class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 헬스체크 등은 열어둘 수 있다(선택). 여기선 /mcp 만 보호.
        if request.url.path.startswith("/mcp"):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer ") or auth[7:] != API_TOKEN:
                return JSONResponse(
                    {"error": "unauthorized", "detail": "유효한 Bearer 토큰이 필요합니다"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)


if __name__ == "__main__":
    # FastMCP 가 만든 streamable-http Starlette 앱을 가져와 미들웨어를 끼운다.
    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)

    print("SECURE HTTP 서버 시작 → http://127.0.0.1:8000/mcp")
    print(f"   필요한 헤더:  Authorization: Bearer {API_TOKEN}")
    uvicorn.run(app, host="127.0.0.1", port=8000)
