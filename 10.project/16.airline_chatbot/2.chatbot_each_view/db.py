"""
SQLite 데이터 레이어 — 항공편 / 예약 / 히스토리.

테이블:
  flights        : 항공편 카탈로그 (편명, 출발/도착, 시각, 좌석/가격)
  bookings       : 예약 (사용자, 항공편, 상태)
  booking_log    : 모든 상태 변경 이력 (예약 → 취소 등 + 행위자 / 시각)
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
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            code        TEXT    NOT NULL UNIQUE,
            origin      TEXT    NOT NULL,
            dest        TEXT    NOT NULL,
            depart_at   TIMESTAMP NOT NULL,
            seats_left  INTEGER NOT NULL,
            price       INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT    NOT NULL,
            flight_id   INTEGER NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'BOOKED',     -- BOOKED / CANCELED
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (flight_id) REFERENCES flights(id)
        );
        CREATE TABLE IF NOT EXISTS booking_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id  INTEGER NOT NULL,
            action      TEXT    NOT NULL,                       -- CREATE / CANCEL
            actor       TEXT    NOT NULL,                       -- 사용자 ID 또는 'admin'
            at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        );
        """)
        # 데모 데이터 — 처음 한 번만
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
                "INSERT INTO flights (code, origin, dest, depart_at, seats_left, price) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                demo,
            )
            c.commit()


# ─── 항공편 조회 ───────────────────────────────────────────
def search_flights(origin: str | None = None, dest: str | None = None):
    q = "SELECT * FROM flights WHERE 1=1"
    args = []
    if origin:
        q += " AND origin = ?"; args.append(origin.upper())
    if dest:
        q += " AND dest = ?";   args.append(dest.upper())
    q += " ORDER BY depart_at"
    with get_conn() as c:
        return [dict(r) for r in c.execute(q, args)]


def get_flight(flight_id: int):
    with get_conn() as c:
        row = c.execute("SELECT * FROM flights WHERE id=?", (flight_id,)).fetchone()
        return dict(row) if row else None


# ─── 예약 / 취소 ───────────────────────────────────────────
def create_booking(user_id: str, flight_id: int) -> dict:
    with get_conn() as c:
        flight = c.execute("SELECT * FROM flights WHERE id=?", (flight_id,)).fetchone()
        if not flight:
            return {"error": f"항공편 id={flight_id} 없음"}
        if flight["seats_left"] <= 0:
            return {"error": f"{flight['code']} 잔여 좌석 없음"}

        cur = c.execute(
            "INSERT INTO bookings (user_id, flight_id) VALUES (?, ?)",
            (user_id, flight_id),
        )
        booking_id = cur.lastrowid
        c.execute("UPDATE flights SET seats_left = seats_left - 1 WHERE id=?", (flight_id,))
        c.execute(
            "INSERT INTO booking_log (booking_id, action, actor) VALUES (?, 'CREATE', ?)",
            (booking_id, user_id),
        )
        c.commit()
        return {"ok": True, "booking_id": booking_id, "flight_code": flight["code"]}


def cancel_booking(booking_id: int, actor: str) -> dict:
    with get_conn() as c:
        b = c.execute("SELECT * FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if not b:
            return {"error": f"예약 id={booking_id} 없음"}
        if b["status"] != "BOOKED":
            return {"error": f"이미 {b['status']} 상태"}
        c.execute("UPDATE bookings SET status='CANCELED' WHERE id=?", (booking_id,))
        c.execute("UPDATE flights SET seats_left = seats_left + 1 WHERE id=?", (b["flight_id"],))
        c.execute(
            "INSERT INTO booking_log (booking_id, action, actor) VALUES (?, 'CANCEL', ?)",
            (booking_id, actor),
        )
        c.commit()
        return {"ok": True}


# ─── 사용자 / 관리자 조회 ──────────────────────────────────
def user_bookings(user_id: str):
    with get_conn() as c:
        rows = c.execute(
            "SELECT b.*, f.code, f.origin, f.dest, f.depart_at, f.price "
            "FROM bookings b JOIN flights f ON b.flight_id = f.id "
            "WHERE b.user_id = ? ORDER BY b.created_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def all_bookings():
    with get_conn() as c:
        rows = c.execute(
            "SELECT b.*, f.code, f.origin, f.dest, f.depart_at "
            "FROM bookings b JOIN flights f ON b.flight_id = f.id "
            "ORDER BY b.created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def booking_history(booking_id: int):
    with get_conn() as c:
        rows = c.execute(
            "SELECT * FROM booking_log WHERE booking_id=? ORDER BY at",
            (booking_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def stats():
    with get_conn() as c:
        return {
            "flights":       c.execute("SELECT COUNT(*) FROM flights").fetchone()[0],
            "bookings_total":c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],
            "bookings_active":c.execute("SELECT COUNT(*) FROM bookings WHERE status='BOOKED'").fetchone()[0],
            "bookings_canceled":c.execute("SELECT COUNT(*) FROM bookings WHERE status='CANCELED'").fetchone()[0],
        }
