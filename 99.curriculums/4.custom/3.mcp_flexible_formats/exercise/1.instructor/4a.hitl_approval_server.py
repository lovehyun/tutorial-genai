"""
6번 실습(HITL)이 쓰는 지원 서버 — 이 파일 자체는 실습 대상이 아니다.
안전한 도구(list_files, read_file)와 위험한 도구(delete_file, send_email)가 섞여 있다.
이 서버는 아무 것도 막지 않는다 — 안전장치는 클라이언트(4b.hitl_approval_client.py) 쪽 몫이다.

원본: 8.mcp/4.langchain/6.human_in_loop/server.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocServer")

DOCS = {
    "report.txt": "1분기 매출 보고서 — 전년 대비 12% 성장",
    "todo.md": "- MCP 예제 정리\n- 발표자료 준비",
    "old_backup.zip": "(2019년 백업 파일, 크기 2.3GB)",
}
SENT_MAILS = []


@mcp.tool()
def list_files() -> str:
    """문서함에 있는 파일 목록을 조회한다."""
    if not DOCS:
        return "문서함이 비어 있습니다."
    return "\n".join(f"- {name}" for name in DOCS)


@mcp.tool()
def read_file(name: str) -> str:
    """문서함에서 파일 하나의 내용을 읽는다."""
    if name not in DOCS:
        return f"'{name}' 파일이 없습니다. list_files 로 목록을 먼저 확인하세요."
    return DOCS[name]


@mcp.tool()
def delete_file(name: str) -> str:
    """문서함에서 파일을 삭제한다. 되돌릴 수 없다."""
    if name not in DOCS:
        return f"'{name}' 파일이 없습니다."
    del DOCS[name]
    return f"'{name}' 삭제 완료. 남은 파일 {len(DOCS)}개."


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """지정한 수신자에게 이메일을 발송한다. 한 번 나가면 회수할 수 없다."""
    SENT_MAILS.append({"to": to, "subject": subject, "body": body})
    return f"'{to}' 에게 메일 발송 완료 (제목: {subject})"


if __name__ == "__main__":
    mcp.run()


# ─── 실행 결과 (2026-08-12) ────────────────────────────────────
# 이 서버는 4b.hitl_approval_client.py / 4cx.hitl_auto_approve.py 가 stdio 로 자동 실행한다 —
# 단독 실행 시 대기 상태로 멈춰 있는 게 정상. 클라이언트 쪽 결과는 그 두 파일 하단 참고.
