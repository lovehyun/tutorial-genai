# notify_server.py — 사람에게 알림을 보내는 MCP 서버 (위험 — 한 번 나가면 회수 불가)
#
# 계정 변경은 그나마 되돌릴 수 있지만, 발송된 메일/메시지는 회수할 수 없다.
# 그래서 2·3단계에서 승인 대상으로 분류한다.
#
# 실제로 메일이 나가지는 않는다 — DB 의 notifications 테이블에 기록만 남긴다.

from mcp.server.fastmcp import FastMCP

import store

store.init()
mcp = FastMCP("Notify")


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """
    이메일을 발송한다. 발송 후에는 회수할 수 없다.

    Args:
        to: 수신자 이메일 주소
        subject: 제목
        body: 본문

    Returns:
        발송 결과 메시지
    """
    conn = store.connect()
    conn.execute(
        "INSERT INTO notifications (kind, target, subject, body, sent_at) VALUES (?,?,?,?,?)",
        ("email", to, subject, body, store.now()),
    )
    conn.commit()
    conn.close()
    return f"메일 발송 완료 — {to} / 제목: {subject}"


@mcp.tool()
def post_message(channel: str, text: str) -> str:
    """
    사내 메신저 채널에 메시지를 게시한다. 게시 후에는 회수할 수 없다.

    Args:
        channel: 채널명 (예: '#general', '#dev')
        text: 게시할 내용

    Returns:
        게시 결과 메시지
    """
    conn = store.connect()
    conn.execute(
        "INSERT INTO notifications (kind, target, subject, body, sent_at) VALUES (?,?,?,?,?)",
        ("message", channel, "", text, store.now()),
    )
    conn.commit()
    conn.close()
    return f"메시지 게시 완료 — {channel}"


@mcp.tool()
def list_sent() -> str:
    """
    지금까지 발송된 알림 기록을 조회한다. (읽기 전용 — 안전)

    Returns:
        발송 시각·종류·수신자·제목 목록
    """
    conn = store.connect()
    rows = conn.execute(
        "SELECT * FROM notifications ORDER BY id DESC LIMIT 20"
    ).fetchall()
    conn.close()

    if not rows:
        return "발송된 알림이 없습니다."

    return "\n".join(
        f"{r['sent_at']} | {r['kind']} | {r['target']} | {r['subject'] or r['body'][:30]}"
        for r in rows
    )


if __name__ == "__main__":
    mcp.run()
