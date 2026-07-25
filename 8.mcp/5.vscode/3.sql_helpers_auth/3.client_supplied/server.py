"""
케이스 3 — 클라이언트가 접속정보를 제공하고, 서버는 '프록시'만 한다.

    클라이언트 ──[접속 DSN 을 세션에 제공]──▶ 서버(무자격증명) ──▶ 클라가 지정한 DB
                                                                 (shop.db? hr.db? 원격?)

- 서버는 **아무 자격증명도 갖지 않는다.** 어디에 붙을지는 전적으로 클라이언트가 정한다.
- MCP 서버 = "네가 준 DB 에 쿼리해 주는" 범용 프록시 인터페이스.

■ 보안 핵심 — 비밀은 '툴 인자'로 받지 않는다
  run_query(dsn, sql) 처럼 DSN(비번 포함)을 **도구 인자로 받으면 LLM 컨텍스트·전사에 남는다(유출).**
  그래서 접속정보는 **세션 밖 채널**로 받는다:
    - stdio: 서버를 띄울 때 환경변수(CLIENT_DSN) 로  ← 이 데모
    - HTTP : 접속 시 헤더(예: X-DB-DSN)로 (README 참고)
  → 도구 인자에는 오직 'sql' 만. 자격증명은 절대 안 흐른다.

준비:  python ../init_db.py  →  pip install mcp  →  python client.py
"""

import os
import sys

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlcommon  # noqa: E402

MAX_ROWS = 200
mcp = FastMCP("sql-auth-proxy")


def connect():
    """클라이언트가 세션 밖 채널(여기선 CLIENT_DSN 환경변수)로 준 DSN 으로 접속."""
    dsn = os.getenv("CLIENT_DSN")
    if not dsn:
        raise RuntimeError("클라이언트가 접속정보(CLIENT_DSN)를 제공하지 않았습니다")

    if dsn.startswith("sqlite:"):                 # sqlite:<파일경로> (단순화 DSN)
        return sqlcommon.open_ro(os.path.abspath(dsn[len("sqlite:"):]))

    if dsn.startswith(("postgres://", "postgresql://")):
        import psycopg                            # 표준 URL 그대로 (user/pass/ssl 포함)
        return psycopg.connect(dsn)

    if dsn.startswith("mysql://"):
        import pymysql                            # 실전: URL 파싱 후 연결
        raise NotImplementedError("mysql DSN 파싱은 실전에서 구현 (pymysql)")

    raise ValueError(f"알 수 없는 DSN: {dsn[:20]}...")


def _with(fn):
    conn = connect()
    try:
        return fn(conn)
    finally:
        conn.close()


@mcp.tool()
def which_db() -> str:
    """지금 서버가 (클라이언트 지정으로) 붙어 있는 대상과 테이블을 알려준다."""
    dsn = os.getenv("CLIENT_DSN", "(없음)")
    tables = _with(sqlcommon.table_names)
    # DSN 을 그대로 노출하지 않도록 스킴만 보여준다(비번 유출 방지)
    scheme = dsn.split(":", 1)[0]
    return f"대상 스킴={scheme}, 테이블={', '.join(tables)}"


@mcp.tool()
def list_tables() -> str:
    """클라이언트가 지정한 DB 의 테이블 목록."""
    return "\n".join(f"- {t}" for t in _with(sqlcommon.table_names))


@mcp.tool()
def run_query(sql: str) -> str:
    """읽기 전용 SQL 실행. (인자는 sql 뿐 — 접속정보는 여기로 안 들어온다)"""
    try:
        return _with(lambda c: sqlcommon.run_select(c, sql, MAX_ROWS))
    except ValueError as e:
        return f"[거부] {e}"
    except Exception as e:
        return f"[오류] {type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run()
