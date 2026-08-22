"""
케이스 1 — 서버가 자격증명을 '다 관리' (모든 호출자는 동일 접근).

    클라이언트 ──(신원 불필요)──▶ 서버 ──[.env 의 자격증명으로 로그인]──▶ DB

- 서버 `.env` 에 접속정보가 있고, connect() 가 그 값으로 DB 에 인증한다.
- 누가 부르든 같은 계정으로 붙으므로 '모두 동일 접근'.
- ★ 여기가 "원격 DB 인증을 실제로 어떻게 하냐"의 답이 사는 곳:
  아래 connect() 가 sqlite / postgres / mysql / 접속URL / 클라우드 IAM 을 모두 보여준다.
  (이 데모는 sqlite 로 실행되지만, 나머지 분기 코드는 그대로 실전에서 쓴다.)

준비:  python ../init_db.py   →   pip install mcp python-dotenv   →   python client.py
"""

import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlcommon  # noqa: E402

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
MAX_ROWS = int(os.getenv("SQL_MAX_ROWS", "200"))

mcp = FastMCP("sql-auth-managed")


# ─────────────────────────────────────────────────────────────
# connect() — '서버가 인증하는' 자리. DB 종류별 자격증명 처리.
#             이 데모는 sqlite 로 돌지만, 나머지 분기는 실전 코드 그대로다.
# ─────────────────────────────────────────────────────────────
def connect():
    if DB_TYPE == "sqlite":
        path = os.getenv("SQLITE_PATH", os.path.join(HERE, "..", "shop.db"))
        return sqlcommon.open_ro(os.path.abspath(path))

    # (참고) 접속 URL 을 통째로 받은 경우 — Neon/Heroku/Railway 등
    url = os.getenv("DATABASE_URL")
    if url and DB_TYPE in ("postgres", "postgresql"):
        import psycopg
        return psycopg.connect(url)          # user/pass/ssl 이 URL 안에 다 있음

    if DB_TYPE in ("postgres", "postgresql"):
        import psycopg
        password = os.getenv("PGPASSWORD")
        # (참고) 클라우드 IAM 인증 — 정적 비번 대신 단기 토큰 발급:
        #   import boto3
        #   password = boto3.client("rds").generate_db_auth_token(
        #       DBHostname=os.getenv("PGHOST"), Port=5432, DBUsername=os.getenv("PGUSER"))
        return psycopg.connect(
            host=os.getenv("PGHOST"), port=int(os.getenv("PGPORT", "5432")),
            user=os.getenv("PGUSER"), password=password, dbname=os.getenv("PGDATABASE"),
            sslmode=os.getenv("PGSSLMODE", "prefer"),      # 관리형 DB 는 'require'
        )

    if DB_TYPE in ("mysql", "mariadb"):
        import pymysql
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST"), port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER"), password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"), charset="utf8mb4",
        )

    raise ValueError(f"지원하지 않는 DB_TYPE: {DB_TYPE!r}")


def _with(fn):
    conn = connect()
    try:
        return fn(conn)
    finally:
        conn.close()


@mcp.tool()
def list_tables() -> str:
    """테이블 목록."""
    return "\n".join(f"- {t}" for t in _with(sqlcommon.table_names))


@mcp.tool()
def describe_table(table: str) -> str:
    """테이블 컬럼 구조."""
    return _with(lambda c: sqlcommon.describe(c, table))


@mcp.tool()
def run_query(sql: str) -> str:
    """읽기 전용 SQL 실행(SELECT/WITH/EXPLAIN). 모든 호출자가 동일 권한."""
    try:
        return _with(lambda c: sqlcommon.run_select(c, sql, MAX_ROWS))
    except ValueError as e:
        return f"[거부] {e}"
    except Exception as e:
        return f"[SQL 오류] {type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run()
