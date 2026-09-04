# itops_server.py — 계정·권한을 '실제로 바꾸는' MCP 서버 (위험)
#
# ── 중요: 이 서버는 아무 것도 막지 않는다 ───────────────────────
#   grant_access("E1001", "prod-db") 를 부르면 그냥 준다. 확인 절차가 없다.
#   평범한 사내 시스템 API 가 원래 그렇다.
#   → 그래서 승인 게이트는 이 서버가 아니라 '이 서버를 쓰는 쪽'(app.py)이 건다.
#     서버를 고칠 수 없는 상황(다른 팀 소유, 외부 벤더)이 실제로 흔하다.

from mcp.server.fastmcp import FastMCP

import store

store.init()
mcp = FastMCP("ITOps")


def _employee(conn, employee_id):
    return conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()


@mcp.tool()
def create_account(employee_id: str, username: str) -> str:
    """
    직원의 사내 계정을 생성한다. (되돌리려면 관리자 승인이 필요하다)

    Args:
        employee_id: 사번 (예: 'E1001')
        username: 만들 계정 아이디 (예: 'chulsoo')

    Returns:
        생성 결과 메시지
    """
    conn = store.connect()
    if not _employee(conn, employee_id):
        conn.close()
        return f"'{employee_id}' 사번의 직원이 없습니다."

    if conn.execute("SELECT 1 FROM accounts WHERE employee_id = ?", (employee_id,)).fetchone():
        conn.close()
        return f"{employee_id} 는 이미 계정이 있습니다. 중복 생성하지 않았습니다."

    if conn.execute("SELECT 1 FROM accounts WHERE username = ?", (username,)).fetchone():
        conn.close()
        return f"'{username}' 은 이미 사용 중인 아이디입니다. 다른 아이디를 제안하세요."

    conn.execute("INSERT INTO accounts VALUES (?,?,?,?)",
                 (employee_id, username, "active", store.now()))
    conn.commit()
    conn.close()
    return f"계정 생성 완료 — {employee_id} → '{username}' (상태 active)"


@mcp.tool()
def grant_access(employee_id: str, group: str) -> str:
    """
    직원에게 접근 그룹 권한을 부여한다. 되돌리려면 revoke_access 가 필요하다.

    Args:
        employee_id: 사번 (예: 'E1001')
        group: 그룹명. list_groups 로 확인 (email/vpn/github/prod-db/payroll)

    Returns:
        부여 결과 메시지. 위험도가 high 인 그룹이면 경고를 함께 돌려준다
    """
    conn = store.connect()
    if not _employee(conn, employee_id):
        conn.close()
        return f"'{employee_id}' 사번의 직원이 없습니다."

    if not conn.execute("SELECT 1 FROM accounts WHERE employee_id = ?", (employee_id,)).fetchone():
        conn.close()
        return f"{employee_id} 는 아직 계정이 없습니다. create_account 를 먼저 하세요."

    grp = conn.execute("SELECT * FROM groups WHERE name = ?", (group,)).fetchone()
    if not grp:
        conn.close()
        return f"'{group}' 그룹이 없습니다. list_groups 로 확인하세요."

    if conn.execute("SELECT 1 FROM access WHERE employee_id = ? AND group_name = ?",
                    (employee_id, group)).fetchone():
        conn.close()
        return f"{employee_id} 는 이미 '{group}' 권한이 있습니다."

    conn.execute("INSERT INTO access VALUES (?,?,?)", (employee_id, group, store.now()))
    conn.commit()
    conn.close()

    warn = " ⚠️ 위험도 high 그룹입니다." if grp["risk"] == "high" else ""
    return f"권한 부여 완료 — {employee_id} → '{group}'.{warn}"


@mcp.tool()
def revoke_access(employee_id: str, group: str) -> str:
    """
    직원의 접근 그룹 권한을 회수한다.

    Args:
        employee_id: 사번 (예: 'E1001')
        group: 회수할 그룹명

    Returns:
        회수 결과 메시지
    """
    conn = store.connect()
    cur = conn.execute("DELETE FROM access WHERE employee_id = ? AND group_name = ?",
                       (employee_id, group))
    conn.commit()
    removed = cur.rowcount
    conn.close()

    if not removed:
        return f"{employee_id} 에게 '{group}' 권한이 없어 회수할 것이 없습니다."
    return f"권한 회수 완료 — {employee_id} 의 '{group}' 제거."


@mcp.tool()
def reset_password(employee_id: str) -> str:
    """
    직원 계정의 비밀번호를 임시 비밀번호로 초기화한다. 기존 비밀번호는 즉시 무효가 된다.

    Args:
        employee_id: 사번 (예: 'E1002')

    Returns:
        초기화 결과와 임시 비밀번호
    """
    conn = store.connect()
    acc = conn.execute("SELECT * FROM accounts WHERE employee_id = ?", (employee_id,)).fetchone()
    if not acc:
        conn.close()
        return f"{employee_id} 는 계정이 없어 초기화할 수 없습니다."

    conn.execute("UPDATE accounts SET status = ? WHERE employee_id = ?", ("active", employee_id))
    conn.commit()
    conn.close()
    # 데모용 고정 임시 비밀번호 (실제 시스템이라면 무작위 생성 후 안전한 경로로 전달한다)
    return f"비밀번호 초기화 완료 — {acc['username']} / 임시 비밀번호: Temp-{employee_id}!"


if __name__ == "__main__":
    mcp.run()
