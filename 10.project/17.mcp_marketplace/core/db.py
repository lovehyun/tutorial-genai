"""
SQLite 데이터 레이어 — MCP 레지스트리 + 게이트웨이.

핵심 4개체 (수업 ERD 그대로) + 운영 메타:
  servers        : 등록된 MCP 서버 (id, name, endpoint=내부주소, owner, namespace, 설명)
                   + 운영필드 status / last_seen  (헬스 상태 관리용)
  consumers      : 에이전트(소비자)
  subscriptions  : 컨슈머 ↔ 서버 구독 관계
  tools          : 레지스트리가 서버에서 '자동 수집'한 도구 (inputSchema 포함 — 프록시가 그대로 미러링)

상태 전이(절대 즉시 삭제하지 않음 — 메타는 보존하고 status 만 바꾼다):
  ONLINE  : 최근 ONLINE_SEC 이내 응답
  UNHEALTHY: ONLINE_SEC ~ OFFLINE_SEC
  OFFLINE : OFFLINE_SEC ~ ARCHIVE_SEC 응답 없음
  ARCHIVED: ARCHIVE_SEC 초과 (목록에서 흐리게)
"""

import os
import json
import time
import sqlite3

# DB 경로. 도커에선 DB_PATH=/data/marketplace.db + 볼륨 마운트로 영속화(재시작에도 보존).
DB_PATH = os.getenv("DB_PATH") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "marketplace.db")

# 상태 임계값(초) — 교육용으로 짧게. 운영에선 env 로 늘린다.
ONLINE_SEC = int(os.getenv("HEALTH_ONLINE_SEC", "90"))      # 이 이내면 ONLINE
OFFLINE_SEC = int(os.getenv("HEALTH_OFFLINE_SEC", "300"))    # 이 초과면 OFFLINE
ARCHIVE_SEC = int(os.getenv("HEALTH_ARCHIVE_SEC", "86400"))  # 이 초과면 ARCHIVED

# 프록시 호출 로그 보관 상한(건수 기준). 이 수를 넘으면 가장 오래된 것부터 지운다.
CALLS_MAX = int(os.getenv("CALLS_MAX", "5000"))


def now() -> float:
    return time.time()


def get_conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS servers (
            id          TEXT PRIMARY KEY,            -- 슬러그 (예: 'travel')
            name        TEXT NOT NULL,
            endpoint    TEXT NOT NULL,               -- 게이트웨이가 접속할 '내부' MCP 주소
            owner       TEXT NOT NULL DEFAULT '',    -- 만든 팀
            namespace   TEXT NOT NULL DEFAULT 'default',
            description TEXT NOT NULL DEFAULT '',
            status      TEXT NOT NULL DEFAULT 'UNHEALTHY',
            last_seen   REAL,                        -- 마지막으로 살아있던 시각(epoch)
            registered_at REAL
        );
        CREATE TABLE IF NOT EXISTS consumers (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            owner       TEXT NOT NULL DEFAULT '',
            registered_at REAL
        );
        CREATE TABLE IF NOT EXISTS subscriptions (
            consumer_id TEXT NOT NULL,
            server_id   TEXT NOT NULL,
            PRIMARY KEY (consumer_id, server_id)
        );
        CREATE TABLE IF NOT EXISTS tools (
            server_id     TEXT NOT NULL,
            name          TEXT NOT NULL,
            description   TEXT NOT NULL DEFAULT '',
            input_schema  TEXT NOT NULL DEFAULT '{}', -- JSON 문자열 (프록시가 그대로 노출)
            output_schema TEXT NOT NULL DEFAULT '{}', -- JSON 문자열 (있으면 출력 구조)
            PRIMARY KEY (server_id, name)
        );
        CREATE TABLE IF NOT EXISTS calls (        -- 프록시를 통과한 모든 호출 기록
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ts         REAL,                      -- 호출 시각(epoch)
            server_id  TEXT,
            tool       TEXT,
            via        TEXT,                      -- consumer:<id> / server:<id> / ui
            ok         INTEGER,                   -- 1 성공, 0 실패
            latency_ms INTEGER,
            error      TEXT,                      -- 에러 코드(실패 시)
            args       TEXT,                      -- 입력 인자(JSON, 잘림)
            result     TEXT,                      -- 출력/에러 텍스트(잘림)
            ip         TEXT                       -- 요청자 IP (X-Forwarded-For 우선)
        );
        CREATE INDEX IF NOT EXISTS idx_calls_id ON calls(id DESC);
        CREATE TABLE IF NOT EXISTS demo_seeds (   -- 데모 서버 재등록용 기억(삭제돼도 보존)
            id          TEXT PRIMARY KEY,
            name        TEXT, endpoint TEXT, owner TEXT, namespace TEXT, description TEXT
        );
        """)
        c.commit()


def status_for(last_seen: float | None) -> str:
    """last_seen 으로부터 현재 상태를 계산한다."""
    if not last_seen:
        return "UNHEALTHY"
    age = now() - last_seen
    if age <= ONLINE_SEC:
        return "ONLINE"
    if age <= OFFLINE_SEC:
        return "UNHEALTHY"
    if age <= ARCHIVE_SEC:
        return "OFFLINE"
    return "ARCHIVED"


# ─── 서버(SERVER) ──────────────────────────────────────────
def upsert_server(id, name, endpoint, owner="", namespace="default", description="") -> None:
    with get_conn() as c:
        c.execute(
            """INSERT INTO servers (id, name, endpoint, owner, namespace, description, registered_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                   name=excluded.name, endpoint=excluded.endpoint, owner=excluded.owner,
                   namespace=excluded.namespace, description=excluded.description""",
            (id, name, endpoint, owner, namespace, description, now()),
        )
        c.commit()


def remember_seed(id, name, endpoint, owner="", namespace="demo", description="") -> None:
    """데모 서버 재등록용 기억. 서버를 삭제해도 이 기록은 남아 '데모 다시 등록'에 쓰인다."""
    with get_conn() as c:
        c.execute(
            """INSERT INTO demo_seeds (id, name, endpoint, owner, namespace, description)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET name=excluded.name, endpoint=excluded.endpoint,
                   owner=excluded.owner, namespace=excluded.namespace, description=excluded.description""",
            (id, name, endpoint, owner, namespace, description),
        )
        c.commit()


def get_demo_seeds() -> list[dict]:
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM demo_seeds ORDER BY id")]


def mark_seen(server_id: str) -> None:
    """헬스 체크/하트비트 성공 → 살아있음 기록 + ONLINE."""
    with get_conn() as c:
        c.execute("UPDATE servers SET last_seen=?, status='ONLINE' WHERE id=?", (now(), server_id))
        c.commit()


def recompute_statuses() -> None:
    """모든 서버의 status 를 last_seen 기준으로 재계산 (헬스 폴링 후 호출)."""
    with get_conn() as c:
        for r in c.execute("SELECT id, last_seen FROM servers").fetchall():
            c.execute("UPDATE servers SET status=? WHERE id=?", (status_for(r["last_seen"]), r["id"]))
        c.commit()


def set_tools(server_id: str, tools: list[dict]) -> None:
    """수집한 도구로 통째 교체. tools: [{name, description, input_schema, output_schema}]"""
    with get_conn() as c:
        c.execute("DELETE FROM tools WHERE server_id=?", (server_id,))
        c.executemany(
            """INSERT OR REPLACE INTO tools (server_id, name, description, input_schema, output_schema)
               VALUES (?, ?, ?, ?, ?)""",
            [(server_id, t["name"], t.get("description", ""),
              json.dumps(t.get("input_schema", {}), ensure_ascii=False),
              json.dumps(t.get("output_schema", {}), ensure_ascii=False)) for t in tools],
        )
        c.commit()


def _row_to_server(r) -> dict:
    d = dict(r)
    d["status"] = status_for(d.get("last_seen"))  # 항상 실시간 계산값으로 노출
    d["tools"] = get_tools(d["id"])
    return d


def list_servers() -> list[dict]:
    with get_conn() as c:
        return [_row_to_server(r) for r in c.execute("SELECT * FROM servers ORDER BY id")]


def get_server(server_id: str) -> dict | None:
    with get_conn() as c:
        r = c.execute("SELECT * FROM servers WHERE id=?", (server_id,)).fetchone()
        return _row_to_server(r) if r else None


def all_endpoints() -> list[dict]:
    """헬스 폴링용 — (id, endpoint) 목록."""
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT id, endpoint FROM servers")]


def delete_server(server_id: str) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM tools WHERE server_id=?", (server_id,))
        c.execute("DELETE FROM subscriptions WHERE server_id=?", (server_id,))
        c.execute("DELETE FROM servers WHERE id=?", (server_id,))
        c.commit()


def delete_all_servers() -> int:
    """등록된 모든 서버 + 도구 + 구독을 삭제하고 삭제된 서버 수를 돌려준다.
       데모 재등록용 demo_seeds 는 보존하므로 '데모 서버 다시 등록'은 계속 동작한다."""
    with get_conn() as c:
        n = c.execute("SELECT COUNT(*) FROM servers").fetchone()[0]
        c.execute("DELETE FROM tools")
        c.execute("DELETE FROM subscriptions")
        c.execute("DELETE FROM servers")
        c.commit()
    return n


def get_tools(server_id: str) -> list[dict]:
    with get_conn() as c:
        rows = c.execute(
            "SELECT name, description, input_schema, output_schema FROM tools WHERE server_id=? ORDER BY name",
            (server_id,),
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["input_schema"] = json.loads(d["input_schema"] or "{}")
            d["output_schema"] = json.loads(d["output_schema"] or "{}")
            out.append(d)
        return out


# ─── 컨슈머(CONSUMER) ──────────────────────────────────────
def upsert_consumer(id, name, owner="") -> None:
    with get_conn() as c:
        c.execute(
            """INSERT INTO consumers (id, name, owner, registered_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET name=excluded.name, owner=excluded.owner""",
            (id, name, owner, now()),
        )
        c.commit()


def list_consumers() -> list[dict]:
    with get_conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM consumers ORDER BY id")]


def get_consumer(consumer_id: str) -> dict | None:
    with get_conn() as c:
        r = c.execute("SELECT * FROM consumers WHERE id=?", (consumer_id,)).fetchone()
        return dict(r) if r else None


def delete_consumer(consumer_id: str) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM subscriptions WHERE consumer_id=?", (consumer_id,))
        c.execute("DELETE FROM consumers WHERE id=?", (consumer_id,))
        c.commit()


def delete_all_consumers() -> int:
    """모든 컨슈머 + 그 구독을 삭제하고 삭제된 컨슈머 수를 돌려준다."""
    with get_conn() as c:
        n = c.execute("SELECT COUNT(*) FROM consumers").fetchone()[0]
        c.execute("DELETE FROM subscriptions")
        c.execute("DELETE FROM consumers")
        c.commit()
    return n


# ─── 구독(SUBSCRIPTION) ────────────────────────────────────
def set_subscriptions(consumer_id: str, server_ids: list[str]) -> None:
    with get_conn() as c:
        c.execute("DELETE FROM subscriptions WHERE consumer_id=?", (consumer_id,))
        c.executemany(
            "INSERT OR IGNORE INTO subscriptions (consumer_id, server_id) VALUES (?, ?)",
            [(consumer_id, sid) for sid in server_ids],
        )
        c.commit()


def get_subscriptions(consumer_id: str) -> list[dict]:
    """컨슈머가 구독한 서버 목록(엔드포인트·tools 포함). 게이트웨이/에이전트가 쓰는 핵심 쿼리."""
    with get_conn() as c:
        rows = c.execute(
            """SELECT s.* FROM servers s
               JOIN subscriptions sub ON sub.server_id = s.id
               WHERE sub.consumer_id = ? ORDER BY s.id""",
            (consumer_id,),
        ).fetchall()
        return [_row_to_server(r) for r in rows]


# ─── 호출 로그(CALLS) ──────────────────────────────────────
CALL_TEXT_MAX = int(os.getenv("CALL_TEXT_MAX", "800"))   # 로그에 담는 입력/출력 텍스트 길이 상한


def record_call(server_id, tool, via, ok, latency_ms, error=None, args=None, result=None, ip=None) -> None:
    """프록시를 통과한 호출 1건 기록(요청자 IP·입력 args·출력 result 포함) + 상한 초과분 삭제."""
    if isinstance(args, (dict, list)):
        args = json.dumps(args, ensure_ascii=False)
    with get_conn() as c:
        c.execute(
            """INSERT INTO calls (ts, server_id, tool, via, ok, latency_ms, error, args, result, ip)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (now(), server_id, tool, via, 1 if ok else 0, int(latency_ms), error,
             (args or "")[:CALL_TEXT_MAX] or None, (result or "")[:CALL_TEXT_MAX] or None, ip or "-"),
        )
        # 건수 기준 보관: 최신 CALLS_MAX 개만 남기고 나머지 삭제
        c.execute(
            "DELETE FROM calls WHERE id <= (SELECT MAX(id) FROM calls) - ?", (CALLS_MAX,)
        )
        c.commit()


# 검색 필드 → 대상 컬럼. '통합'은 여러 컬럼을 OR 로 묶어 한 번에 검색.
_CALL_SEARCH_FIELDS = {
    "all":    ["ip", "via", "server_id", "tool"],   # 통합
    "ip":     ["ip"],
    "path":   ["via"],                              # 경로(via)
    "server": ["server_id", "tool"],                # 서버·도구
}


def list_calls(page: int = 1, size: int = 20, q: str = "", field: str = "all") -> dict:
    """요청 로그 페이지네이션. 최신순(id DESC). q/field 로 검색 필터링."""
    page = max(1, page); size = max(1, min(size, 200))
    cols = _CALL_SEARCH_FIELDS.get(field, _CALL_SEARCH_FIELDS["all"])
    q = (q or "").strip()
    where, params = "", []
    if q:
        like = f"%{q}%"
        where = " WHERE (" + " OR ".join(f"{col} LIKE ?" for col in cols) + ")"
        params = [like] * len(cols)
    with get_conn() as c:
        total = c.execute("SELECT COUNT(*) FROM calls" + where, params).fetchone()[0]
        rows = c.execute(
            "SELECT * FROM calls" + where + " ORDER BY id DESC LIMIT ? OFFSET ?",
            params + [size, (page - 1) * size]
        ).fetchall()
    pages = max(1, (total + size - 1) // size)
    return {"items": [dict(r) for r in rows], "total": total,
            "page": page, "size": size, "pages": pages, "q": q, "field": field}


def stats() -> dict:
    """대시보드용 집계 — 서버 상태 분포 + 프록시 호출 통계."""
    servers = list_servers()
    status_counts = {}
    for s in servers:
        status_counts[s["status"]] = status_counts.get(s["status"], 0) + 1
    with get_conn() as c:
        total = c.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
        ok = c.execute("SELECT COUNT(*) FROM calls WHERE ok=1").fetchone()[0]
        avg = c.execute("SELECT AVG(latency_ms) FROM calls WHERE ok=1").fetchone()[0]
        by_server = [dict(r) for r in c.execute(
            """SELECT server_id, COUNT(*) total, SUM(ok) ok FROM calls
               GROUP BY server_id ORDER BY total DESC""")]
        by_tool = [dict(r) for r in c.execute(
            """SELECT server_id, tool, COUNT(*) total FROM calls
               GROUP BY server_id, tool ORDER BY total DESC LIMIT 8""")]
        recent = [dict(r) for r in c.execute(
            "SELECT * FROM calls ORDER BY id DESC LIMIT 8")]
        # 최근 15분, 1분 버킷 추이
        since = now() - 15 * 60
        raw = c.execute("SELECT ts, ok FROM calls WHERE ts >= ?", (since,)).fetchall()
    buckets = [{"t": i, "total": 0, "ok": 0} for i in range(15)]
    for r in raw:
        idx = min(14, int((r["ts"] - since) // 60))
        buckets[idx]["total"] += 1
        buckets[idx]["ok"] += r["ok"]
    return {
        "servers_total": len(servers),
        "status_counts": status_counts,
        "consumers_total": len(list_consumers()),
        "calls_total": total, "calls_ok": ok, "calls_fail": total - ok,
        "success_rate": round(ok / total * 100, 1) if total else None,
        "avg_latency_ms": round(avg, 1) if avg else None,
        "by_server": by_server, "by_tool": by_tool,
        "recent": recent, "timeline": buckets,
    }
