# server.py — 평범한 사내 운영 도구 서버 (악의는 없다)
#
# 문제는 이 서버가 나쁘다는 게 아니라, **위험한 인자를 그대로 받는다**는 것이다.
#   run_command("rm -rf /data")        → 그냥 실행한다
#   query_db("DROP TABLE customers")   → 그냥 지운다
#   read_file("../../etc/passwd")      → 그냥 읽는다
#
# 평범한 사내 API 가 원래 이렇다. 인자를 검사하는 건 이 서버가 아니라
# 이 서버를 쓰는 쪽(클라이언트)의 몫이다 → 3.tool_guard.py
#
# 데이터는 전부 메모리 안의 가짜다. 진짜 셸도, 진짜 DB 도, 진짜 파일도 건드리지 않는다.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("OpsTools")

# ── 가짜 파일 저장소 ────────────────────────────────────────────
FILES = {
    "/data/report.csv": "월,매출\n1,1200\n2,1350",
    "/data/notes.txt": "다음 분기 계획 초안",
    "/data/backup.zip": "(2019년 백업, 2.3GB)",
    "/etc/passwd": "root:x:0:0:root:/root:/bin/bash",          # 있으면 안 되는 곳까지 읽힌다
    "/home/app/.ssh/id_rsa": "-----BEGIN PRIVATE KEY-----(가짜)",
}

# ── 가짜 고객 테이블 — PII 가 들어 있다 (출력 가드 실습용) ──────
#   신용카드 번호는 체크섬만 맞춘 테스트용 번호다 (실제 카드 아님)
CUSTOMERS = [
    {"id": "C001", "name": "김민수", "rrn": "900101-1234567",
     "card": "4539-1488-0343-6467", "phone": "010-1234-5678"},
    {"id": "C002", "name": "이수진", "rrn": "880315-2345678",
     "card": "4916-9983-0301-8471", "phone": "010-9876-5432"},
]


@mcp.tool()
def run_command(command: str) -> str:
    """
    서버에서 셸 명령을 실행한다.

    Args:
        command: 실행할 명령 (예: 'ls /data')

    Returns:
        명령 실행 결과
    """
    cmd = command.strip()

    if cmd.startswith("ls"):
        return "\n".join(sorted(FILES))

    if cmd.startswith("cat "):
        path = cmd[4:].strip()
        return FILES.get(path, f"cat: {path}: 그런 파일이 없습니다")

    # rm 은 검사 없이 그대로 '실행' 한다 — 이게 이 예제의 출발점이다
    if cmd.startswith("rm"):
        target = cmd.split()[-1]
        victims = [f for f in FILES if f.startswith(target.rstrip("/"))] or list(FILES)
        for f in victims:
            FILES.pop(f, None)
        return f"삭제 완료 — {len(victims)}개 파일이 사라졌습니다. 남은 파일 {len(FILES)}개."

    return f"(데모 셸) '{cmd}' 를 실행했다고 가정합니다."


@mcp.tool()
def query_db(sql: str) -> str:
    """
    고객 데이터베이스에 SQL 을 실행한다.

    Args:
        sql: 실행할 SQL (예: 'SELECT * FROM customers')

    Returns:
        조회 결과 또는 실행 결과
    """
    q = sql.strip()
    upper = q.upper()

    if upper.startswith("SELECT"):
        if not CUSTOMERS:
            return "결과 없음 (테이블이 비어 있습니다)"
        header = "id | name | rrn | card | phone"
        rows = [f"{c['id']} | {c['name']} | {c['rrn']} | {c['card']} | {c['phone']}"
                for c in CUSTOMERS]
        return "\n".join([header] + rows)

    # DROP / DELETE 도 검사 없이 그대로 수행한다
    if upper.startswith(("DROP", "TRUNCATE", "DELETE")):
        n = len(CUSTOMERS)
        CUSTOMERS.clear()
        return f"실행 완료 — 고객 {n}건이 삭제되었습니다."

    return f"(데모 DB) '{q}' 를 실행했다고 가정합니다."


@mcp.tool()
def read_file(path: str) -> str:
    """
    서버의 파일을 읽는다.

    Args:
        path: 읽을 파일 경로 (예: '/data/report.csv')

    Returns:
        파일 내용
    """
    # 경로를 전혀 검사하지 않는다 — ../ 든 /etc/ 든 그대로 읽는다
    return FILES.get(path.strip(), f"{path}: 그런 파일이 없습니다")


@mcp.tool()
def list_customers() -> str:
    """고객 목록을 조회한다. (이름·연락처 등 개인정보가 포함된다)"""
    if not CUSTOMERS:
        return "고객 정보가 없습니다."
    return "\n".join(f"{c['id']} {c['name']} {c['phone']} {c['rrn']}" for c in CUSTOMERS)


if __name__ == "__main__":
    mcp.run()
