# app.py — [4b] 자동승인이라도 '고위험 인자'면 다시 물어본다 (인자 수준 guardrail)
#
# ══ 이 폴더는 4단계의 두 변형(a/b) 중 하나다 — ../README.md 참고 ═══════
#   `a.tool_name_only/`의 한계: 자동승인은 '도구 이름' 단위였다. grant_access 를
#   한 번 자동승인하면 email 이든 prod-db 든 그냥 나갔다 — 무슨 그룹을 주는지(인자)는
#   안 보고 무슨 도구를 부르는지(이름)만 봤기 때문이다.
#
# ══ 여기(b)서 더하는 것 ═══════════════════════════════════════
#   jobs.py 의 needs_approval() 에 한 줄 추가 — grant_access 호출의 group 인자가
#   고위험(risk=high, servers/store.py 의 GROUPS 참고)이면, 그 도구가 자동승인
#   목록에 있어도 무시하고 다시 승인을 받는다. 자동승인 등록/해제(a 의) 로직은
#   그대로 두고, '자동승인됐는데 이번엔 봐야 하나' 판단만 인자까지 내려간 것이다.
#
#   화면에서는 이렇게 걸린 승인 카드에 [항상 승인] 버튼을 아예 안 보여준다
#   (job.locked) — 고위험 인자가 섞인 배치를 통째로 자동승인하게 두면
#   guardrail 의미가 없어지기 때문이다.
#
# ══ 파일 구성은 a 와 동일 ════════════════════════════════════
#   jobs.py   ← a 의 것 + [4b] _is_high_risk / needs_approval 수정 / job["locked"]
#   agents.py ← 1~4단계에서 만든 것 그대로 (변경 없음)
#   app.py    ← 화면과 이어지는 부분 (변경 없음 — 포트는 a(5084)와 다른 5085 를 그대로 쓴다.
#               둘 다 켜두고 나란히 비교해도 된다)
#
# 실행:
#   pip install flask langchain langchain-openai langchain-mcp-adapters langgraph \
#               langgraph-checkpoint-sqlite python-dotenv mcp
#   .env 에 OPENAI_API_KEY
#   python app.py     → http://localhost:5085

import os
import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

import agents
import jobs

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "..", "servers")

# DB 현황 패널을 위해 사내 시스템 DB 를 직접 읽는다.
#   ※ 일부러 MCP 를 거치지 않는다 — 에이전트가 '정말로' 바꿨는지를
#     MCP 밖에서 확인해야 검증이 되기 때문이다. (운영자 관리 화면에 해당)
sys.path.insert(0, os.path.abspath(SERVERS))
import store  # noqa: E402


# ══════════════════════════════════════════════════════════════
# DB 현황 — 에이전트가 실제로 바꾼 것을 MCP 밖에서 확인한다
# ══════════════════════════════════════════════════════════════

def db_snapshot() -> dict:
    """계정 / 권한 / 발송 기록을 읽어 화면에 뿌릴 형태로 만든다."""
    conn = store.connect()
    accounts = [dict(r) for r in conn.execute("""
        SELECT a.employee_id, a.username, a.status, e.name
        FROM accounts a LEFT JOIN employees e ON e.id = a.employee_id
        ORDER BY a.created_at
    """)]
    # 권한 줄에도 이름을 붙인다 — 사번(E1001)만 보고는 누군지 알 수 없다
    access = [dict(r) for r in conn.execute("""
        SELECT ac.employee_id, ac.group_name, g.risk, e.name
        FROM access ac
        LEFT JOIN groups g    ON g.name = ac.group_name
        LEFT JOIN employees e ON e.id   = ac.employee_id
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

store.init()                          # DB 패널이 빈 테이블을 읽지 않도록 먼저 보장
main, worker, TOOL_NAMES = jobs.run(agents.build())
jobs.bind(worker)                     # 워커 에이전트를 jobs 모듈에 넣어준다

app = Flask(__name__)
# 채팅 대화 번호. [초기화] 를 누르면 하나 올려서 '새 대화' 로 시작한다.
#   안 그러면 에이전트가 초기화 전 대화를 기억해 "아까 처리했다" 고 답해버린다.
CHAT_SEQ = 0


def chat_config() -> dict:
    return {"configurable": {"thread_id": f"web-{CHAT_SEQ}"}}


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
        config = chat_config()
        snapshot = await main.aget_state(config)
        before = len(snapshot.values.get("messages", []))
        state = await main.ainvoke({"messages": [("user", message)]}, config=config)
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
    """화면 전체가 1초마다 이걸 폴링한다 (작업 + 자동승인 목록 + DB 현황)."""
    return jsonify({
        "jobs": [jobs.public(j) for j in jobs.JOBS.values()],
        "auto": sorted(jobs.AUTO_APPROVED),
        "db": db_snapshot(),
    })


@app.route("/jobs/<job_id>/decide", methods=["POST"])
def decide(job_id):
    """승인 / 항상 승인 / 거부. always=True 면 그 도구를 자동승인 목록에 올린다."""
    job = jobs.JOBS.get(job_id)
    if not job or job["status"] != "waiting":
        return jsonify({"ok": False, "error": "승인 대기 중인 작업이 아닙니다."}), 400

    data = request.json or {}
    approved = bool(data.get("approved"))
    always = bool(data.get("always"))

    if approved and always:
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
    """자동승인 해제 — 다음부터 다시 물어본다."""
    jobs.AUTO_APPROVED.discard(name)
    return jsonify({"ok": True, "auto": sorted(jobs.AUTO_APPROVED)})


@app.route("/db/reset", methods=["POST"])
def reset_db():
    """
    데모를 처음 상태로 되돌린다. 실습을 여러 번 돌릴 때 쓴다.

    셋을 함께 되돌려야 한다 — DB 만 지우면 앱 상태와 어긋나 버린다:
      · DB      : 시드 상태로
      · 작업 목록: 비운다 (지워진 계정을 가리키는 기록이 남으면 혼란스럽다)
      · 채팅 대화: 새 대화로 (안 그러면 "아까 온보딩 했잖아요" 라며 일을 안 한다)

    자동승인 목록은 그대로 둔다 — 데이터가 아니라 '정책' 이라서
    초기화 뒤에도 자동승인이 유지되는지 실습으로 확인할 수 있어야 한다.
    """
    global CHAT_SEQ
    store.reset()
    jobs.clear()
    CHAT_SEQ += 1
    return jsonify({"ok": True, "db": db_snapshot()})


if __name__ == "__main__":
    print("MCP 도구:", TOOL_NAMES)
    print("자동승인: (비어 있음 — [항상 승인] 을 누르면 채워진다)")
    print("고위험 인자 guardrail: grant_access 의 group 이 risk=high 면 자동승인과 무관하게 항상 재확인")
    print("→ http://localhost:5085")
    app.run(port=5085, debug=False, threaded=True)
