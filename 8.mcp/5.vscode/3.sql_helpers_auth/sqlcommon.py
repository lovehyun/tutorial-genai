"""
sqlcommon — 세 인증 케이스가 공유하는 DB 유틸(가드·포맷·조회).

세 서버(1.server_managed / 2.per_user_scope / 3.client_supplied)는
'인증/스코프' 부분만 서로 다르고, 아래 로직은 완전히 동일하다.
→ 여기 한 벌만 두고 각 server.py 가 import 한다 (레이어 분리: 도구로직 ↔ 인증).

각 server.py 상단에서:
    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import sqlcommon
"""

import re
import sqlite3

# ── 읽기 전용 가드 ────────────────────────────────────────────
_ALLOWED_FIRST = ("select", "with", "explain")
_WRITE = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|truncate|merge|"
    r"attach|detach|grant|revoke|reindex|vacuum|pragma|call)\b",
    re.IGNORECASE,
)


def ensure_readonly(sql: str) -> str:
    cleaned = re.sub(r"--[^\n]*", " ", sql)
    cleaned = re.sub(r"/\*.*?\*/", " ", cleaned, flags=re.DOTALL).strip()
    if not cleaned:
        raise ValueError("빈 쿼리")
    if ";" in cleaned.rstrip(";"):
        raise ValueError("여러 문장 금지(세미콜론 다중 쿼리)")
    first = cleaned.split(None, 1)[0].lower()
    if first not in _ALLOWED_FIRST:
        raise ValueError(f"읽기 전용만 허용(SELECT/WITH/EXPLAIN). '{first}' 거부.")
    if _WRITE.search(cleaned):
        raise ValueError("데이터 변경/DDL 키워드 감지 → 거부(읽기 전용).")
    return cleaned.rstrip(";")


def referenced_tables(sql: str) -> set[str]:
    """FROM/JOIN 뒤의 테이블 이름을 뽑는다(사용자별 스코프 검사용, 단순판)."""
    return {m.lower() for m in re.findall(r"(?:from|join)\s+([A-Za-z_]\w*)", sql, re.IGNORECASE)}


# ── 포맷 ─────────────────────────────────────────────────────
def format_rows(cols, rows, truncated=False) -> str:
    if not cols:
        return "(결과 컬럼 없음)"
    if not rows:
        return "(행 없음)"
    widths = [len(str(c)) for c in cols]
    srows = [[("NULL" if v is None else str(v)) for v in r] for r in rows]
    for r in srows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(cell))
    line = lambda cells: " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells))
    out = [line(cols), "-+-".join("-" * w for w in widths)] + [line(r) for r in srows]
    if truncated:
        out.append("... (상한 초과분 잘림)")
    return "\n".join(out)


# ── sqlite 조회 (connect = 0-인자 커넥션 팩토리) ────────────────
def open_ro(path: str) -> sqlite3.Connection:
    """읽기 전용 모드로 sqlite 열기(uri) — DB 파일 자체를 못 바꾸게."""
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def table_names(conn) -> list[str]:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    return [r[0] for r in cur.fetchall()]


def describe(conn, table: str) -> str:
    if table not in table_names(conn):
        return f"그런 테이블 없음: {table!r}"
    cur = conn.execute(f'PRAGMA table_info("{table}")')
    rows = [[r["name"], r["type"], r["notnull"], r["pk"]] for r in cur.fetchall()]
    return format_rows(["column", "type", "notnull", "pk"], rows)


def run_select(conn, sql: str, max_rows: int = 200) -> str:
    safe = ensure_readonly(sql)
    cur = conn.execute(safe)
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchmany(max_rows + 1)
    return format_rows(cols, rows[:max_rows], truncated=len(rows) > max_rows)
