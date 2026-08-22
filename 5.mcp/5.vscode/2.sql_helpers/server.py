"""
sql-helper — 내 DB 를 MCP 서버로 노출한다. "자연어 → SQL → 결과 행".

클라이언트(Claude Code / Copilot / Cline …)의 LLM 이:
  1) list_tables / describe_table 로 스키마를 파악하고
  2) 스스로 SQL 을 작성해 run_query 로 실행하고
  3) 돌아온 행으로 답을 만든다.
→ 사용자는 "도시별 총 매출 알려줘" 처럼 '자연어' 로만 물으면 된다.

지원 DB (접속정보 .env 만 바꾸면 도구 인터페이스는 동일):
  - sqlite    (로컬 파일)         ← 이 예제의 '완성본', 표준 라이브러리만으로 동작
  - postgresql (원격)             ← pip install "psycopg[binary]"
  - mysql / mariadb (원격)        ← pip install pymysql

■ 안전장치 (중요)
  - run_query 는 **읽기 전용**: SELECT / WITH / EXPLAIN 만 허용, 그 외(INSERT·UPDATE·DELETE·DROP…)는 거부.
  - 결과는 MAX_ROWS 로 제한(과다 출력 방지).
  - 그래도 운영에서는 **읽기 전용 DB 계정**으로 접속하는 걸 권장(코드 가드는 2차 방어).

준비:
  python init_db.py          # 샘플 sqlite 생성 (sqlite 경로면 필수)
  pip install mcp python-dotenv
  # (원격 DB 쓸 때만) pip install "psycopg[binary]"  또는  pip install pymysql

접속정보:
  같은 폴더 .env (없으면 sqlite ./sample.db 기본값). .env.example 참고.
"""

import os
import re
import sqlite3

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
MAX_ROWS = int(os.getenv("SQL_MAX_ROWS", "200"))

mcp = FastMCP("sql-helper")


# ─────────────────────────────────────────────────────────────
# 1) 연결 — DB 종류별 커넥션 팩토리 (여기만 종류별로 다르다)
# ─────────────────────────────────────────────────────────────
def connect():
    if DB_TYPE == "sqlite":
        path = os.getenv("SQLITE_PATH", os.path.join(HERE, "sample.db"))
        if not os.path.exists(path):
            raise FileNotFoundError(f"sqlite DB 없음: {path}  →  먼저 `python init_db.py` 실행")
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn

    if DB_TYPE in ("postgres", "postgresql"):
        import psycopg                     # pip install "psycopg[binary]"
        return psycopg.connect(
            host=os.getenv("PGHOST", "localhost"),
            port=int(os.getenv("PGPORT", "5432")),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            dbname=os.getenv("PGDATABASE"),
            # 원격은 TLS 권장:  sslmode=os.getenv("PGSSLMODE", "require")
        )

    if DB_TYPE in ("mysql", "mariadb"):
        import pymysql                     # pip install pymysql
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            charset="utf8mb4",
            # 원격은 TLS 권장:  ssl={"ca": os.getenv("MYSQL_SSL_CA")}
        )

    raise ValueError(f"지원하지 않는 DB_TYPE: {DB_TYPE!r} (sqlite / postgres / mysql)")


def _quote_ident(name: str) -> str:
    """식별자 인용 — mysql 은 backtick, 그 외는 표준 큰따옴표."""
    if DB_TYPE in ("mysql", "mariadb"):
        return "`" + name.replace("`", "``") + "`"
    return '"' + name.replace('"', '""') + '"'


# ─────────────────────────────────────────────────────────────
# 2) 스키마 조회 — DB 종류별 introspection SQL
# ─────────────────────────────────────────────────────────────
def _fetch(sql: str, params=()):
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(MAX_ROWS + 1)
        return cols, rows
    finally:
        conn.close()


def _list_table_names() -> list[str]:
    if DB_TYPE == "sqlite":
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        _, rows = _fetch(sql)
    elif DB_TYPE in ("postgres", "postgresql"):
        sql = ("SELECT table_name FROM information_schema.tables "
               "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name")
        _, rows = _fetch(sql)
    else:  # mysql
        sql = ("SELECT table_name FROM information_schema.tables "
               "WHERE table_schema = DATABASE() ORDER BY table_name")
        _, rows = _fetch(sql)
    return [r[0] for r in rows]


def _format(cols, rows, truncated: bool) -> str:
    if not cols:
        return "(결과 컬럼 없음)"
    if not rows:
        return "(행 없음)"
    widths = [len(str(c)) for c in cols]
    srows = [[("NULL" if v is None else str(v)) for v in row] for row in rows]
    for row in srows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    line = lambda cells: " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells))
    out = [line(cols), "-+-".join("-" * w for w in widths)]
    out += [line(r) for r in srows]
    if truncated:
        out.append(f"... (MAX_ROWS={MAX_ROWS} 초과분 잘림)")
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────
# 3) 읽기 전용 SQL 가드
# ─────────────────────────────────────────────────────────────
_ALLOWED_FIRST = ("select", "with", "explain")
_WRITE_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|merge|"
    r"attach|detach|grant|revoke|reindex|vacuum|pragma|call)\b",
    re.IGNORECASE,
)


def _ensure_readonly(sql: str) -> str:
    # 주석 제거(-- 라인, /* */ 블록)
    cleaned = re.sub(r"--[^\n]*", " ", sql)
    cleaned = re.sub(r"/\*.*?\*/", " ", cleaned, flags=re.DOTALL).strip()
    if not cleaned:
        raise ValueError("빈 쿼리")
    # 다중 문장 금지 (SELECT ...; DROP ... 같은 스택 공격 차단)
    if ";" in cleaned.rstrip(";"):
        raise ValueError("여러 문장은 허용되지 않습니다(세미콜론으로 구분된 다중 쿼리 금지)")
    first = cleaned.split(None, 1)[0].lower()
    if first not in _ALLOWED_FIRST:
        raise ValueError(f"읽기 전용만 허용됩니다. '{first}' 로 시작하는 쿼리는 거부(SELECT/WITH/EXPLAIN 만).")
    # WITH ... DELETE/UPDATE 같은 우회도 차단
    if _WRITE_KEYWORDS.search(cleaned):
        raise ValueError("데이터 변경/DDL 키워드가 감지되어 거부되었습니다(읽기 전용).")
    return cleaned.rstrip(";")


# ─────────────────────────────────────────────────────────────
# 4) MCP 도구
# ─────────────────────────────────────────────────────────────
@mcp.tool()
def list_tables() -> str:
    """현재 DB 의 테이블 목록을 반환한다."""
    names = _list_table_names()
    return "테이블:\n" + "\n".join(f"- {n}" for n in names) if names else "테이블이 없습니다."


@mcp.tool()
def describe_table(table: str) -> str:
    """특정 테이블의 컬럼 구조(이름/타입/NULL여부)를 반환한다."""
    if table not in _list_table_names():          # 화이트리스트 검증(식별자 주입 방지)
        return f"그런 테이블이 없습니다: {table!r}. list_tables 로 확인하세요."
    if DB_TYPE == "sqlite":
        cols, rows = _fetch(f"PRAGMA table_info({_quote_ident(table)})")
        # PRAGMA: cid,name,type,notnull,dflt_value,pk
        header = ["column", "type", "notnull", "pk"]
        data = [[r["name"], r["type"], r["notnull"], r["pk"]] for r in rows]
        return _format(header, data, truncated=False)
    else:
        sql = ("SELECT column_name, data_type, is_nullable "
               "FROM information_schema.columns "
               "WHERE table_name = %s "
               + ("AND table_schema = DATABASE() " if DB_TYPE in ("mysql", "mariadb")
                  else "AND table_schema = 'public' ")
               + "ORDER BY ordinal_position")
        cols, rows = _fetch(sql, (table,))
        return _format(cols, rows, truncated=False)


@mcp.tool()
def preview_table(table: str, limit: int = 5) -> str:
    """테이블의 앞부분 몇 행을 미리 본다(기본 5행)."""
    if table not in _list_table_names():
        return f"그런 테이블이 없습니다: {table!r}."
    limit = max(1, min(int(limit), MAX_ROWS))
    cols, rows = _fetch(f"SELECT * FROM {_quote_ident(table)} LIMIT {limit}")
    return _format(cols, rows[:limit], truncated=False)


@mcp.tool()
def run_query(sql: str) -> str:
    """읽기 전용 SQL(SELECT/WITH/EXPLAIN)을 실행하고 결과 행을 표로 반환한다.
    조인·집계·서브쿼리 모두 가능. 변경/DDL 쿼리는 거부된다."""
    try:
        safe_sql = _ensure_readonly(sql)
    except ValueError as e:
        return f"[거부] {e}"
    try:
        cols, rows = _fetch(safe_sql)
    except Exception as e:
        return f"[SQL 오류] {type(e).__name__}: {e}"
    truncated = len(rows) > MAX_ROWS
    return _format(cols, rows[:MAX_ROWS], truncated)


@mcp.resource("schema://database")
def schema_overview() -> str:
    """DB 전체 스키마 개요(테이블별 컬럼) — LLM 이 SQL 을 짤 때 참고하는 지도."""
    lines = [f"DB_TYPE = {DB_TYPE}", ""]
    for t in _list_table_names():
        lines.append(f"[{t}]")
        lines.append(describe_table(t))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()   # 기본 stdio — 클라이언트가 자식 프로세스로 띄운다
