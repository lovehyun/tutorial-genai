"""
케이스 2 — 서버가 자격증명을 관리하되, '호출자를 인증'해 사용자별로 다른 범위를 준다.

    사용자A(analyst) ─[Bearer tok-analyst]─┐
    사용자B(admin)   ─[Bearer tok-admin]───┤─▶ 하나의 서버 ─▶ 같은 DB
                                            └   그러나 A는 customers(PII) 못 봄, B는 다 봄

■ 왜 HTTP + Bearer 인가
  로컬 stdio 서버는 사용자가 1명(=나)이라 '사용자별'이 성립 안 한다.
  하나의 서버가 '여러 사용자'를 서빙하려면 원격 HTTP + 사용자별 토큰이라야
  "이 요청 = 누구"를 알 수 있다.

■ 2단계 방어
  authN(인증): 미들웨어가 Authorization 토큰이 유효한지 → 아니면 401.
  authZ(인가): 각 도구가 그 토큰의 '사용자 스코프'로 접근 가능한 테이블을 제한.

■ 혼동된 대리인(confused deputy) 방지
  스코프는 '인증된 토큰'에만 바인딩한다. 요청 본문이나 LLM 이 말한 값으로 고르지 않는다.

준비:  python ../init_db.py   →   pip install mcp uvicorn   →   (터미널1) python server.py / (터미널2) python client.py
"""

import os
import sys

import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp.server.fastmcp import Context, FastMCP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlcommon  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(HERE, "..", "shop.db"))
MAX_ROWS = 200

# 토큰 → 사용자/스코프. 실전에선 OAuth 토큰 검증 + DB 의 사용자·권한 테이블에서 조회.
#   tables="*" 는 전체 허용.  집합이면 그 테이블만.
TOKENS = {
    "tok-analyst": {"user": "analyst", "tables": {"products", "orders", "order_items"}},  # customers(PII) 제외
    "tok-admin":   {"user": "admin",   "tables": "*"},                                     # 전체
}

mcp = FastMCP("sql-auth-scope")


def _connect():
    # 서버가 보유한 자격증명으로 접속(모두 같은 DB). 사용자 구분은 '스코프'로만.
    return sqlcommon.open_ro(DB_PATH)


def _profile(ctx: Context) -> dict:
    """이번 요청의 Bearer 토큰 → 사용자 프로필. (요청 헤더에서 직접, 요청 본문 아님)"""
    req: Request = ctx.request_context.request
    auth = (req.headers.get("authorization") if req else "") or ""
    token = auth[7:] if auth.lower().startswith("bearer ") else ""
    prof = TOKENS.get(token)
    if not prof:
        raise PermissionError("유효한 Bearer 토큰이 아닙니다")
    return prof


def _allowed(prof: dict) -> set | str:
    return prof["tables"]


@mcp.tool()
def whoami(ctx: Context) -> str:
    """내 신원과 접근 가능한 테이블을 알려준다."""
    p = _profile(ctx)
    scope = "전체" if p["tables"] == "*" else ", ".join(sorted(p["tables"]))
    return f"user={p['user']}  접근가능={scope}"


@mcp.tool()
def list_tables(ctx: Context) -> str:
    """내 스코프에서 볼 수 있는 테이블만 반환한다."""
    prof = _profile(ctx)
    allowed = _allowed(prof)
    def q(conn):
        names = sqlcommon.table_names(conn)
        return names if allowed == "*" else [n for n in names if n in allowed]
    conn = _connect()
    try:
        names = q(conn)
    finally:
        conn.close()
    return f"[{prof['user']}] 볼 수 있는 테이블:\n" + "\n".join(f"- {n}" for n in names)


@mcp.tool()
def run_query(sql: str, ctx: Context) -> str:
    """읽기 전용 SQL 실행 — 단, 내 스코프 밖 테이블을 건드리면 거부된다."""
    try:
        prof = _profile(ctx)
    except PermissionError as e:
        return f"[인증거부] {e}"
    allowed = _allowed(prof)
    try:
        safe = sqlcommon.ensure_readonly(sql)
    except ValueError as e:
        return f"[거부] {e}"
    if allowed != "*":
        used = sqlcommon.referenced_tables(safe)
        blocked = used - set(allowed)
        if blocked:
            return f"[인가거부] user={prof['user']} 는 {', '.join(sorted(blocked))} 접근 불가 (허용: {', '.join(sorted(allowed))})"
    conn = _connect()
    try:
        return f"[{prof['user']}]\n" + sqlcommon.run_select(conn, safe, MAX_ROWS)
    except Exception as e:
        return f"[SQL 오류] {type(e).__name__}: {e}"
    finally:
        conn.close()


# ── authN 미들웨어: 토큰이 아예 유효하지 않으면 401 (transport 레벨) ──
class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            auth = request.headers.get("Authorization", "")
            token = auth[7:] if auth.lower().startswith("bearer ") else ""
            if token not in TOKENS:
                return JSONResponse({"error": "unauthorized"}, status_code=401,
                                    headers={"WWW-Authenticate": "Bearer"})
        return await call_next(request)


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"shop.db 없음 → 먼저 `python ../init_db.py`  ({DB_PATH})")
        sys.exit(1)
    app = mcp.streamable_http_app()
    app.add_middleware(BearerAuthMiddleware)
    print("SCOPE 서버 시작 → http://127.0.0.1:8000/mcp")
    print("  토큰: tok-analyst(customers 제외) / tok-admin(전체)")

    # ── 데모(로컬)는 평문 http. 실제 배포 = HTTPS(TLS). 아래 둘 중 하나 (데모와 공존 불가) ──
    uvicorn.run(app, host="127.0.0.1", port=8000)

    # (배포 A, 권장) TLS 는 앞단 nginx/로드밸런서가 종단하고 내부는 평문 http 유지:
    #     클라 ──https──▶ nginx ──http──▶ 이 uvicorn(위 코드 그대로)
    #     → 서버 파이썬 코드 변경 0. 클라만 https:// 로 붙는다. (레포: 3.anthropic/.../3.simple_net_remote/nginx)
    #
    # (배포 B) uvicorn 이 직접 TLS 종단 — 인증서 파일을 직접 물릴 때:
    #     uvicorn.run(app, host="0.0.0.0", port=8443,
    #                 ssl_certfile="/etc/ssl/fullchain.pem",
    #                 ssl_keyfile="/etc/ssl/privkey.pem")
    #     → 엔드포인트가 https://<host>:8443/mcp 가 된다.
