"""
SQLite 데이터 레이어 — #2 + 상담 채팅 (consultations / consultation_messages).

추가 테이블:
  consultations          : 상담 세션 (REQUESTED / ACTIVE / CLOSED)
  consultation_messages  : 상담 안에서 오간 메시지들 (사용자↔관리자)
"""

import sqlite3
import datetime as dt

DB_PATH = "airline.db"


def get_conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with get_conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT NOT NULL UNIQUE,
            origin TEXT NOT NULL, dest TEXT NOT NULL,
            depart_at TIMESTAMP NOT NULL,
            seats_left INTEGER NOT NULL, price INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL, flight_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'BOOKED',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        );
        CREATE TABLE IF NOT EXISTS booking_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL, action TEXT NOT NULL,
            actor TEXT NOT NULL, at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        );

        -- 상담 세션
        CREATE TABLE IF NOT EXISTS consultations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT    NOT NULL,
            topic       TEXT,
            status      TEXT    NOT NULL DEFAULT 'REQUESTED',   -- REQUESTED / ACTIVE / CLOSED
            admin_id    TEXT,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at   TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS consultation_messages (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            consultation_id INTEGER NOT NULL,
            sender          TEXT    NOT NULL,                   -- 'user' / 'admin' / 'system'
            text            TEXT    NOT NULL,
            at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultation_id) REFERENCES consultations(id)
        );
        """)
        if not c.execute("SELECT 1 FROM flights LIMIT 1").fetchone():
            now = dt.datetime.now().replace(microsecond=0)
            demo = [
                ("KE001", "ICN", "NRT", now + dt.timedelta(days=1, hours=2),  120,  280000),
                ("KE002", "ICN", "NRT", now + dt.timedelta(days=2),           80,  310000),
                ("OZ501", "ICN", "LAX", now + dt.timedelta(days=3, hours=5),  60, 1450000),
                ("OZ502", "GMP", "CJU", now + dt.timedelta(days=1),          150,  85000),
                ("KE100", "ICN", "CDG", now + dt.timedelta(days=4),           40, 1620000),
            ]
            c.executemany(
                "INSERT INTO flights (code, origin, dest, depart_at, seats_left, price) VALUES (?,?,?,?,?,?)",
                demo,
            )
            c.commit()


# ─── 항공편 / 예약 (2단계와 동일) ─────────────────────────
def search_flights(origin=None, dest=None):
    q = "SELECT * FROM flights WHERE 1=1"; args = []
    if origin: q += " AND origin = ?"; args.append(origin.upper())
    if dest:   q += " AND dest = ?";   args.append(dest.upper())
    q += " ORDER BY depart_at"
    with get_conn() as c:
        return [dict(r) for r in c.execute(q, args)]


def create_booking(user_id, flight_id):
    with get_conn() as c:
        flight = c.execute("SELECT * FROM flights WHERE id=?", (flight_id,)).fetchone()
        if not flight: return {"error": f"flight id={flight_id} 없음"}
        if flight["seats_left"] <= 0: return {"error": f"{flight['code']} 매진"}
        cur = c.execute("INSERT INTO bookings (user_id, flight_id) VALUES (?,?)", (user_id, flight_id))
        bid = cur.lastrowid
        c.execute("UPDATE flights SET seats_left=seats_left-1 WHERE id=?", (flight_id,))
        c.execute("INSERT INTO booking_log (booking_id, action, actor) VALUES (?,'CREATE',?)", (bid, user_id))
        c.commit()
        return {"ok": True, "booking_id": bid, "flight_code": flight["code"]}


def cancel_booking(booking_id, actor):
    with get_conn() as c:
        b = c.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if not b: return {"error": f"예약 {booking_id} 없음"}
        if b["status"] != "BOOKED": return {"error": f"이미 {b['status']}"}
        c.execute("UPDATE bookings SET status='CANCELED' WHERE id=?", (booking_id,))
        c.execute("UPDATE flights SET seats_left=seats_left+1 WHERE id=?", (b["flight_id"],))
        c.execute("INSERT INTO booking_log (booking_id, action, actor) VALUES (?,'CANCEL',?)", (booking_id, actor))
        c.commit()
        return {"ok": True}


def user_bookings(uid):
    with get_conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT b.*, f.code, f.origin, f.dest, f.depart_at, f.price "
            "FROM bookings b JOIN flights f ON b.flight_id=f.id "
            "WHERE b.user_id=? ORDER BY b.created_at DESC", (uid,))]


def all_bookings():
    with get_conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT b.*, f.code, f.origin, f.dest, f.depart_at "
            "FROM bookings b JOIN flights f ON b.flight_id=f.id "
            "ORDER BY b.created_at DESC")]


def booking_history(bid):
    with get_conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM booking_log WHERE booking_id=? ORDER BY at", (bid,))]


def stats():
    with get_conn() as c:
        return {
            "flights":           c.execute("SELECT COUNT(*) FROM flights").fetchone()[0],
            "bookings_total":    c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
            "bookings_active":   c.execute("SELECT COUNT(*) FROM bookings WHERE status='BOOKED'").fetchone()[0],
            "bookings_canceled": c.execute("SELECT COUNT(*) FROM bookings WHERE status='CANCELED'").fetchone()[0],
            "consult_pending":   c.execute("SELECT COUNT(*) FROM consultations WHERE status='REQUESTED'").fetchone()[0],
            "consult_active":    c.execute("SELECT COUNT(*) FROM consultations WHERE status='ACTIVE'").fetchone()[0],
        }


# ─── 상담 (consultations) ────────────────────────────────
def request_consultation(user_id: str, topic: str = "") -> dict:
    """사용자가 상담사 연결 요청"""
    with get_conn() as c:
        # 이미 활성/대기 중인 게 있으면 재사용
        existing = c.execute(
            "SELECT * FROM consultations WHERE user_id=? AND status IN ('REQUESTED','ACTIVE') LIMIT 1",
            (user_id,),
        ).fetchone()
        if existing:
            return dict(existing)

        cur = c.execute(
            "INSERT INTO consultations (user_id, topic) VALUES (?, ?)", (user_id, topic)
        )
        cid = cur.lastrowid
        c.execute(
            "INSERT INTO consultation_messages (consultation_id, sender, text) VALUES (?,'system',?)",
            (cid, "상담사 연결을 요청했습니다. 잠시만 기다려주세요."),
        )
        c.commit()
        return dict(c.execute("SELECT * FROM consultations WHERE id=?", (cid,)).fetchone())


def accept_consultation(consultation_id: int, admin_id: str) -> dict:
    with get_conn() as c:
        row = c.execute("SELECT * FROM consultations WHERE id=?", (consultation_id,)).fetchone()
        if not row: return {"error": "상담 없음"}
        if row["status"] != "REQUESTED": return {"error": f"이미 {row['status']}"}
        c.execute("UPDATE consultations SET status='ACTIVE', admin_id=? WHERE id=?", (admin_id, consultation_id))
        c.execute(
            "INSERT INTO consultation_messages (consultation_id, sender, text) VALUES (?,'system',?)",
            (consultation_id, f"상담사({admin_id})가 연결되었습니다."),
        )
        c.commit()
        return {"ok": True}


def close_consultation(consultation_id: int, by: str) -> dict:
    with get_conn() as c:
        c.execute(
            "UPDATE consultations SET status='CLOSED', closed_at=CURRENT_TIMESTAMP WHERE id=?",
            (consultation_id,),
        )
        c.execute(
            "INSERT INTO consultation_messages (consultation_id, sender, text) VALUES (?,'system',?)",
            (consultation_id, f"상담이 종료되었습니다. ({by})"),
        )
        c.commit()
    return {"ok": True}


def get_consultation(consultation_id: int):
    with get_conn() as c:
        row = c.execute("SELECT * FROM consultations WHERE id=?", (consultation_id,)).fetchone()
        return dict(row) if row else None


def list_consultations(status: str | None = None):
    with get_conn() as c:
        if status:
            rows = c.execute("SELECT * FROM consultations WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = c.execute("SELECT * FROM consultations WHERE status IN ('REQUESTED','ACTIVE') ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]


def user_active_consultation(user_id: str):
    """사용자의 현재 진행 중인 상담 (없으면 None)"""
    with get_conn() as c:
        row = c.execute(
            "SELECT * FROM consultations WHERE user_id=? AND status IN ('REQUESTED','ACTIVE') "
            "ORDER BY created_at DESC LIMIT 1", (user_id,),
        ).fetchone()
        return dict(row) if row else None


# 메시지
def add_message(consultation_id: int, sender: str, text: str) -> dict:
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO consultation_messages (consultation_id, sender, text) VALUES (?,?,?)",
            (consultation_id, sender, text),
        )
        c.commit()
        return {"ok": True, "message_id": cur.lastrowid}


def list_messages(consultation_id: int, since_id: int = 0):
    with get_conn() as c:
        rows = c.execute(
            "SELECT * FROM consultation_messages WHERE consultation_id=? AND id>? ORDER BY id",
            (consultation_id, since_id),
        ).fetchall()
        return [dict(r) for r in rows]
