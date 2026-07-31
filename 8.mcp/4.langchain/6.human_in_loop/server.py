# server.py — 안전한 도구와 위험한 도구가 섞여 있는 MCP 서버
#
# ── 이 서버의 포인트: 서버는 아무 것도 막지 않는다 ──────────────
#   delete_file 도 send_email 도, 부르면 그냥 실행된다. 확인 절차가 없다.
#   즉 '남이 만든 평범한 MCP 서버' 를 흉내낸 것이다.
#   → 그래서 안전장치를 걸 곳은 클라이언트뿐이다. (1.approval_gate.py / 2.risky_only.py)
#
#   ※ 비교: 1.basic/4.advanced/3.elicitation 의 서버는 ctx.elicit() 으로 서버가 직접 되묻는다.
#     그건 서버 저자가 협조해 줄 때만 가능한 방식이고, 이 폴더는 그 반대 상황을 다룬다.
#
# 데이터는 전부 메모리 안의 가짜다 — 실제 파일이 지워지거나 메일이 나가지 않는다.
#
# 실행: 클라이언트가 stdio 로 자동 실행하므로 직접 띄울 필요 없다.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocServer")

# ── 가짜 문서함 (메모리) ────────────────────────────────────────
DOCS = {
    "report.txt": "1분기 매출 보고서 — 전년 대비 12% 성장",
    "todo.md": "- MCP 예제 정리\n- 발표자료 준비",
    "old_backup.zip": "(2019년 백업 파일, 크기 2.3GB)",
}
SENT_MAILS = []


# ── 안전한 도구 (읽기 전용 — 되돌릴 필요가 없다) ────────────────

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


# ── 위험한 도구 (되돌릴 수 없거나 외부로 나간다) ────────────────

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
    mcp.run()   # stdio — 클라이언트가 자식 프로세스로 띄운다
