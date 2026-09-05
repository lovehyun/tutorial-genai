# 1단계 — 출발점

MCP 서버 3개에 챗봇을 붙이기만 한다. 승인 절차는 없다.

## 구성

| 파일 | 내용 |
|---|---|
| `app.py` | `MultiServerMCPClient` 로 서버 3개 → `create_agent` → `/chat` |
| `templates/index.html` | 채팅 UI + 호출한 도구 표시 |
| `static/style.css` | **2~4단계용 클래스까지 미리 들어 있다** — 이후 단계에서 안 건드려도 된다 |

MCP 서버(`../servers/`)는 **1~4단계 내내 한 줄도 바뀌지 않는다.**

## 이 단계의 한계 → 2단계로 가는 이유

```
(계정·email·vpn 을 먼저 만든 뒤) "김철수한테 prod-db 권한 줘"  →  그냥 준다. 아무도 안 묻는다.
```

운영 DB 접근 권한이 대화 한 줄로 나간다.
되돌릴 수 없는 작업 앞에 사람을 세워야 한다 → `2.hitl_approve/CHANGES.md`
