# app.py — [4단계] 한 번 승인한 기능은 다시 묻지 않는다 (자동승인) + 결과를 눈으로 확인
#
# ══ 3단계의 한계 ═══════════════════════════════════════════════
#   온보딩을 열 명 하면 create_account 승인을 열 번 누른다. 매번 같은 판단인데도.
#   이게 '승인 피로' 다. 사람이 지치면 결국 내용을 안 보고 누르게 되고,
#   그 순간 승인 게이트는 있으나 마나가 된다.
#
# ══ 이 단계에서 더하는 것 ═══════════════════════════════════════
#   ① 자동승인 — 승인할 때 [항상 승인] 을 고르면 그 도구가 목록에 올라가고 다음부터 안 묻는다
#   ② 자동승인 목록을 화면에 띄운다 — 무엇을 위임했는지 안 보이면 위험하다. 해제도 가능
#   ③ DB 현황 패널 — 에이전트가 실제로 무엇을 바꿨는지 MCP 밖에서 직접 확인
#
#   ②③ 이 없으면 자동승인은 그냥 '가드레일 끄기' 다.
#   무엇을 자동으로 넘겼고 그 결과 무엇이 바뀌었는지 볼 수 있어야 통제가 성립한다.
#
# ══ 파일이 셋으로 나뉘었다 ══════════════════════════════════════
#   3단계까지는 app.py 하나였는데 400줄이 넘어갔다. 코드를 바꾼 게 아니라 자리만 옮겼다.
#
#     jobs.py   ← 3단계에서 만든 것 (이벤트 루프 · 작업 저장소 · 워커 루프)
#                 + [4단계] AUTO_APPROVED / needs_approval
#     agents.py ← 1~3단계에서 만든 것 (MCP 설정 · 체크포인터 · 에이전트 조립). 4단계 변경 없음
#     app.py    ← 화면과 이어지는 부분. 4단계에서 새로 배우는 것이 여기 모인다
#
# ══ 자동승인의 단위 ════════════════════════════════════════════
#   '도구 이름' 단위다. create_account 를 자동승인하면 모든 계정 생성이 통과한다.
#   단순하지만 범위가 너무 넓다 — grant_access 를 한 번 자동승인하면
#   어떤 그룹을 주든 전부 통과한다. prod-db 도 예외가 아니다.
#   (더 정교하게 가는 법은 CHANGES.md 참고)
#
# 실행:
#   pip install flask langchain langchain-openai langchain-mcp-adapters langgraph \
#               langgraph-checkpoint-sqlite python-dotenv mcp
#   .env 에 OPENAI_API_KEY
#   python app.py     → http://localhost:5084

import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

import agents
import jobs

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "servers")

# [4단계] DB 현황 패널을 위해 사내 시스템 DB 를 직접 읽는다.
#   ※ 일부러 MCP 를 거치지 않는다 — 에이전트가 '정말로' 바꿨는지를
#     MCP 밖에서 확인해야 검증이 되기 때문이다. (운영자 관리 화면에 해당)
sys.path.insert(0, os.path.abspath(SERVERS))
import store  # noqa: E402


# ══════════════════════════════════════════════════════════════
# [4단계] DB 현황 — 에이전트가 실제로 바꾼 것을 MCP 밖에서 확인한다
# ══════════════════════════════════════════════════════════════

def db_snapshot() -> dict:
    """계정 / 권한 / 발송 기록을 읽어 화면에 뿌릴 형태로 만든다."""
    conn = store.connect()
    accounts = [dict(r) for r in conn.execute("""
        SELECT a.employee_id, a.username, a.status, e.name
        FROM accounts a LEFT JOIN employees e ON e.id = a.employee_id
        ORDER BY a.created_at
    """)]
    access = [dict(r) for r in conn.execute("""
        SELECT ac.employee_id, ac.group_name, g.risk
        FROM access ac LEFT JOIN groups g ON g.name = ac.group_name
        ORDER BY ac.employee_id, ac.group_name
    """)]
    sent = [dict(r) for r in conn.execute("""
        SELECT kind, target, subject, sent_at FROM notifications
        ORDER BY id DESC LIMIT 10
    """)]
    conn.close()
    return {"accounts": accounts, "access": access, "sent": sent}


# ══════════════════════════════════════════════════════════════
# 조립
# ══════════════════════════════════════════════════════════════

store.init()                          # [4단계] DB 패널이 빈 테이블을 읽지 않도록 먼저 보장
main, worker, TOOL_NAMES = jobs.run(agents.build())
jobs.bind(worker)                     # 워커 에이전트를 jobs 모듈에 넣어준다

app = Flask(__name__)
CHAT_CONFIG = {"configurable": {"thread_id": "web"}}


# ══════════════════════════════════════════════════════════════
# 엔드포인트
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", tools=TOOL_NAMES, safe=sorted(jobs.SAFE_TOOLS))


@app.route("/chat", methods=["POST"])
def chat():
    message = (request.json or {}).get("message", "").strip()
    if not message:
        return jsonify({"reply": "메시지를 입력하세요.", "trace": []})

    async def turn():
        snapshot = await main.aget_state(CHAT_CONFIG)
        before = len(snapshot.values.get("messages", []))
        state = await main.ainvoke({"messages": [("user", message)]}, config=CHAT_CONFIG)
        trace = []
        for m in state["messages"][before:]:
            for c in (getattr(m, "tool_calls", None) or []):
                trace.append(f"→ {c['name']}({c['args']})")
            if m.type == "tool":
                trace.append(f"← {m.name}: {str(m.content)[:200]}")
        return {"reply": state["messages"][-1].content, "trace": trace}

    return jsonify(jobs.run(turn()))


@app.route("/state")
def state():
    """
    화면 전체가 1초마다 이걸 폴링한다.
    [4단계] 3단계의 /jobs 가 작업만 주던 것을, 자동승인 목록 + DB 현황까지 함께 준다.
    """
    return jsonify({
        "jobs": [jobs.public(j) for j in jobs.JOBS.values()],
        "auto": sorted(jobs.AUTO_APPROVED),
        "db": db_snapshot(),
    })


@app.route("/jobs/<job_id>/decide", methods=["POST"])
def decide(job_id):
    """승인 / 항상 승인 / 거부. [4단계] always=True 면 그 도구를 자동승인 목록에 올린다."""
    job = jobs.JOBS.get(job_id)
    if not job or job["status"] != "waiting":
        return jsonify({"ok": False, "error": "승인 대기 중인 작업이 아닙니다."}), 400

    data = request.json or {}
    approved = bool(data.get("approved"))
    always = bool(data.get("always"))                       # [4단계] 새 필드

    if approved and always:                                 # [4단계]
        for c in (job["pending"] or []):
            if c["name"] not in jobs.SAFE_TOOLS:
                jobs.AUTO_APPROVED.add(c["name"])
                job["log"].append(f"⚡ 자동승인 등록: {c['name']}")

    job["_decision"] = approved
    event = job["_event"]
    if event:
        # Event 는 백그라운드 루프의 것이므로, 그 루프 안에서 set 해야 안전하다
        jobs.LOOP.call_soon_threadsafe(event.set)
    return jsonify({"ok": True})


@app.route("/auto/<name>/revoke", methods=["POST"])
def revoke_auto(name):
    """[4단계] 자동승인 해제 — 다음부터 다시 물어본다."""
    jobs.AUTO_APPROVED.discard(name)
    return jsonify({"ok": True, "auto": sorted(jobs.AUTO_APPROVED)})


if __name__ == "__main__":
    print("MCP 도구:", TOOL_NAMES)
    print("자동승인: (비어 있음 — [항상 승인] 을 누르면 채워진다)")
    print("→ http://localhost:5084")
    app.run(port=5084, debug=False, threaded=True)
