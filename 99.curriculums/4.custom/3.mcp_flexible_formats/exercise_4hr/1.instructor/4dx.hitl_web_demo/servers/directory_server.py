# directory_server.py — 사내 인사/계정 '조회' MCP 서버 (전부 읽기 전용 = 안전)
#
# 이 서버의 도구는 아무 것도 바꾸지 않는다. 그래서 승인 없이 자동으로 통과시킨다.
# (2·3단계에서 SAFE 로 분류되는 쪽)

from mcp.server.fastmcp import FastMCP

import store

store.init()
mcp = FastMCP("Directory")


@mcp.tool()
def find_employee(keyword: str) -> str:
    """
    직원을 이름·이메일·사번으로 검색한다.

    Args:
        keyword: 검색어. 이름 일부('김철'), 이메일, 사번('E1001') 모두 가능

    Returns:
        사번·이름·이메일·부서·직급·입사일
    """
    conn = store.connect()
    rows = conn.execute(
        "SELECT * FROM employees WHERE id LIKE ? OR name LIKE ? OR email LIKE ?",
        (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"),
    ).fetchall()
    conn.close()

    if not rows:
        return f"'{keyword}' 로 검색된 직원이 없습니다."

    return "\n".join(
        f"{r['id']} | {r['name']} | {r['email']} | {r['dept']} {r['title']} | 입사 {r['joined']}"
        for r in rows
    )


@mcp.tool()
def get_account_status(employee_id: str) -> str:
    """
    직원의 계정 상태와 현재 가진 접근 권한을 조회한다.

    Args:
        employee_id: 사번 (예: 'E1001')

    Returns:
        계정 유무·상태·보유 그룹 목록
    """
    conn = store.connect()
    emp = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if not emp:
        conn.close()
        return f"'{employee_id}' 사번의 직원이 없습니다. find_employee 로 먼저 확인하세요."

    acc = conn.execute("SELECT * FROM accounts WHERE employee_id = ?", (employee_id,)).fetchone()
    groups = [r["group_name"] for r in conn.execute(
        "SELECT group_name FROM access WHERE employee_id = ? ORDER BY group_name", (employee_id,)
    )]
    conn.close()

    if not acc:
        return f"{emp['name']}({employee_id}): 계정 없음 — 아직 생성되지 않았습니다."

    have = ", ".join(groups) if groups else "(없음)"
    return f"{emp['name']}({employee_id}): 계정 '{acc['username']}' / 상태 {acc['status']} / 권한: {have}"


@mcp.tool()
def list_groups() -> str:
    """
    부여 가능한 접근 그룹 목록을 위험도와 함께 조회한다.

    Returns:
        그룹명 · 설명 · 위험도(low/medium/high)
    """
    conn = store.connect()
    rows = conn.execute("SELECT * FROM groups ORDER BY risk DESC, name").fetchall()
    conn.close()
    return "\n".join(f"{r['name']} [{r['risk']}] — {r['description']}" for r in rows)


if __name__ == "__main__":
    mcp.run()
