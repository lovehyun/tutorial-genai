# store.py — 세 MCP 서버가 함께 보는 사내 시스템 DB (SQLite)
#
# ── 왜 파일 DB 인가 ─────────────────────────────────────────────
#   MCP 서버 세 개는 서로 다른 프로세스다. 메모리를 공유할 수 없다.
#   itops 가 계정을 만들었는데 directory 로 조회하면 안 보이면 데모가 성립하지 않는다.
#   → 같은 SQLite 파일을 보게 해서 '사내 시스템들이 같은 DB 를 바라보는' 실제 구조를 흉내낸다.
#
#   초기화하고 싶으면 이 폴더의 ops.db 파일을 지우면 된다 (다음 실행 때 다시 시드된다).

import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ops.db")

# 접근 그룹 — risk 가 high 인 것은 사람이 승인을 망설이게 만드는 장치다
GROUPS = [
    ("email",    "사내 메일 계정",              "low"),
    ("vpn",      "사내망 VPN 접속",             "medium"),
    ("github",   "소스 저장소 읽기/쓰기",        "medium"),
    ("prod-db",  "운영 데이터베이스 직접 접근",   "high"),
    ("payroll",  "급여 시스템 조회",             "high"),
]

EMPLOYEES = [
    ("E1001", "김철수", "chulsoo@example.com", "개발팀",   "사원",  "2026-08-01"),
    ("E1002", "이영희", "younghee@example.com", "마케팅팀", "대리",  "2024-03-02"),
    ("E1003", "박민수", "minsoo@example.com",  "재무팀",   "과장",  "2021-07-15"),
    # E1004~E1009 는 각각 2단계·3a·3b·3c·4a·4b 데모 전용 온보딩 대상이다. 같은 신입을
    # 두 변형이 같이 쓰면, 먼저 실습한 변형에서 이미 만든 계정이 나중 변형에서
    # "이미 있습니다"로 no-op 될 뿐 아니라, 모델이 get_account_status 로 먼저 확인하고
    # "이미 다 되어 있다"며 온보딩 도구를 아예 안 부를 수도 있다 — 그러면 승인 카드 자체가
    # 안 뜨는, 데모가 완전히 안 서는 상황이 된다. 그래서 변형마다 계정 없는 신입을 따로 둔다.
    ("E1004", "최유진", "yujin@example.com",   "인사팀",   "사원",  "2026-08-01"),
    ("E1005", "정다은", "daeun@example.com",   "영업팀",   "사원",  "2026-08-01"),
    ("E1008", "한소연", "soyeon@example.com",  "IT팀",     "사원",  "2026-08-01"),
    ("E1009", "윤도현", "dohyun@example.com",  "물류팀",   "사원",  "2026-08-01"),
    ("E1006", "강태호", "taeho@example.com",   "디자인팀", "사원",  "2026-08-01"),
    ("E1007", "오지훈", "jihoon@example.com",  "총무팀",   "사원",  "2026-08-01"),
]


def connect() -> sqlite3.Connection:
    """세 서버가 각자 열어 쓰는 커넥션. timeout 은 동시 쓰기 때 잠깐 기다려 주기 위함."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    """테이블을 만들고, 비어 있으면 시드 데이터를 넣는다. 각 서버가 시작할 때 호출한다."""
    conn = connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY, name TEXT, email TEXT,
            dept TEXT, title TEXT, joined TEXT
        );
        CREATE TABLE IF NOT EXISTS groups (
            name TEXT PRIMARY KEY, description TEXT, risk TEXT
        );
        CREATE TABLE IF NOT EXISTS accounts (
            employee_id TEXT PRIMARY KEY, username TEXT,
            status TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS access (
            employee_id TEXT, group_name TEXT, granted_at TEXT,
            PRIMARY KEY (employee_id, group_name)
        );
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT, target TEXT, subject TEXT, body TEXT, sent_at TEXT
        );
    """)

    if not conn.execute("SELECT 1 FROM employees LIMIT 1").fetchone():
        conn.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?)", EMPLOYEES)
        conn.executemany("INSERT INTO groups VALUES (?,?,?)", GROUPS)
        # 이영희·박민수만 이미 계정이 있다 — 신입 7명(E1001, E1004~E1009)은 계정 없는
        # 상태에서 시작한다 (변형마다 다른 신입을 온보딩 대상으로 쓴다)
        now = datetime.now().isoformat(timespec="seconds")
        conn.executemany(
            "INSERT INTO accounts VALUES (?,?,?,?)",
            [("E1002", "younghee", "active", now), ("E1003", "minsoo", "active", now)],
        )
        conn.executemany(
            "INSERT INTO access VALUES (?,?,?)",
            [("E1002", "email", now), ("E1002", "vpn", now),
             ("E1003", "email", now), ("E1003", "payroll", now)],
        )
        conn.commit()

    conn.close()


def reset() -> None:
    """
    모든 테이블을 비우고 시드 데이터를 다시 넣는다 (데모 초기화용).

    4a·4b 의 [초기화] 버튼이 이걸 부른다. 실습을 여러 번 돌릴 때
    ops.db 파일을 직접 지우지 않고도 처음 상태로 되돌리기 위한 것이다.
    """
    conn = connect()
    conn.executescript("""
        DELETE FROM access;
        DELETE FROM accounts;
        DELETE FROM notifications;
        DELETE FROM employees;
        DELETE FROM groups;
    """)
    try:
        # notifications 의 자동 증가 번호도 1 부터 다시 (없으면 무시)
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'notifications'")
    except Exception:
        pass
    conn.commit()
    conn.close()

    init()      # 테이블이 비었으므로 시드가 다시 들어간다


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")
