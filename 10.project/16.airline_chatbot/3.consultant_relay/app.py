"""
항공 예약 시스템 #3 — 상담사 연결 실시간 채팅 추가.
이 예제: #2 의 챗봇이 한계를 넘는 질문을 받으면 사용자가 "상담사 연결" 을 요청 →
        관리자가 수락하면 사용자 ↔ 관리자 직접 채팅 (폴링 기반).

#2 와의 차이:
  - 챗봇 도구에 request_consultation 추가
  - 상담 REST API: 요청/수락/종료/메시지 송수신
  - UI: 사용자측 상담 패널 / 관리자측 활성 상담 목록 + 채팅
  - 양쪽이 setInterval 폴링으로 새 메시지 가져옴 (2초 간격)
  - WebSocket 까지는 안 가서 단순, 충분
"""

import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

import db

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key")


# ─── 사용자 도구 — 예약 / 취소 / 조회 + 상담 요청 ──────────
def make_user_tools(user_id: str):
    @tool
    def search_flights(origin: str | None = None, dest: str | None = None) -> list[dict]:
        """항공편 검색. origin/dest 는 공항코드(ICN, NRT 등)."""
        return db.search_flights(origin, dest)

    @tool
    def book_flight(flight_id: int) -> dict:
        """flight_id 항공편 예약."""
        return db.create_booking(user_id, flight_id)

    @tool
    def my_bookings() -> list[dict]:
        """내 예약 목록."""
        return db.user_bookings(user_id)

    @tool
    def cancel_my_booking(booking_id: int) -> dict:
        """내 예약을 취소 (본인 것만)."""
        bookings = db.user_bookings(user_id)
        if booking_id not in {b["id"] for b in bookings}:
            return {"error": "본인 예약이 아닙니다"}
        return db.cancel_booking(booking_id, actor=user_id)

    @tool
    def request_consultation(topic: str = "") -> dict:
        """챗봇으로 해결이 어렵거나 사용자가 사람 상담사를 원할 때 호출. topic 은 요청 사유."""
        return db.request_consultation(user_id, topic)

    return [search_flights, book_flight, my_bookings, cancel_my_booking, request_consultation]


USER_PROMPT = """\
당신은 항공 예약 비서입니다.
- 일반적인 예약/조회/취소는 도구로 직접 처리하세요.
- 환불 / 보상 / 분쟁 / 법적 문의 / 챗봇이 답할 수 없는 복잡한 사정은 request_consultation 도구로
  상담사를 연결하세요. topic 에 사용자의 요청 요약을 짧게 적어주세요.
- 사용자가 "상담사 연결해줘", "사람 상담사", "고객센터" 요청 시에도 즉시 request_consultation 호출.
- 한국어로 1~3문장 간결히.
"""


# ─── 관리자 도구 (#2 와 동일) ──────────────────────────────
@tool
def admin_all_bookings() -> list[dict]:
    """전체 예약 목록."""
    return db.all_bookings()

@tool
def admin_stats() -> dict:
    """시스템 통계."""
    return db.stats()

@tool
def admin_booking_history(booking_id: int) -> list[dict]:
    """예약 이력."""
    return db.booking_history(booking_id)

@tool
def admin_force_cancel(booking_id: int) -> dict:
    """강제 취소."""
    return db.cancel_booking(booking_id, actor="admin")


ADMIN_PROMPT = """\
당신은 항공사 운영 관리자를 보조하는 비서입니다.
도구: admin_stats / admin_all_bookings / admin_booking_history(id) / admin_force_cancel(id)
- 변경 작업 전에 id 와 사유 확인
- 한국어 간결히
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
admin_agent = create_react_agent(
    llm, [admin_all_bookings, admin_stats, admin_booking_history, admin_force_cancel],
    prompt=ADMIN_PROMPT, checkpointer=MemorySaver(),
)

USER_AGENTS: dict[str, object] = {}

def get_user_agent(user_id: str):
    if user_id not in USER_AGENTS:
        USER_AGENTS[user_id] = create_react_agent(
            llm, make_user_tools(user_id), prompt=USER_PROMPT, checkpointer=MemorySaver(),
        )
    return USER_AGENTS[user_id]


# ─── 화면 ─────────────────────────────────────────────────
@app.get("/")
def user_view():
    if "user_id" not in session: return render_template("login.html")
    return render_template("user.html", user_id=session["user_id"])

@app.post("/login")
def login():
    uid = request.form.get("user_id", "").strip()
    if uid: session["user_id"] = uid
    return redirect(url_for("user_view"))

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("user_view"))

@app.get("/admin")
def admin_view():
    return render_template("admin.html")


# ─── 항공/예약 API (#2 와 동일) ───────────────────────────
@app.get("/api/flights")
def api_flights():
    return jsonify(db.search_flights(origin=request.args.get("origin"), dest=request.args.get("dest")))

@app.get("/api/my-bookings")
def api_my_bookings():
    uid = session.get("user_id")
    if not uid: return jsonify({"error": "로그인 필요"}), 401
    return jsonify(db.user_bookings(uid))

@app.post("/api/bookings")
def api_book():
    uid = session.get("user_id")
    if not uid: return jsonify({"error": "로그인 필요"}), 401
    flight_id = (request.get_json() or {}).get("flight_id")
    return jsonify(db.create_booking(uid, int(flight_id)))

@app.post("/api/bookings/<int:bid>/cancel")
def api_cancel(bid):
    return jsonify(db.cancel_booking(bid, session.get("user_id") or "admin"))

@app.get("/api/all-bookings")
def api_all_bookings(): return jsonify(db.all_bookings())

@app.get("/api/stats")
def api_stats(): return jsonify(db.stats())

@app.get("/api/bookings/<int:bid>/history")
def api_booking_history(bid): return jsonify(db.booking_history(bid))


# ─── 챗봇 ─────────────────────────────────────────────────
WRITE_TOOLS = {"book_flight", "cancel_my_booking", "admin_force_cancel", "request_consultation"}

def _changed(messages):
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            if any(c["name"] in WRITE_TOOLS for c in m.tool_calls):
                return True
    return False


@app.post("/chat/user")
def chat_user():
    uid = session.get("user_id")
    if not uid: return jsonify({"error": "로그인 필요"}), 401
    msg = (request.get_json() or {}).get("message", "").strip()
    if not msg: return jsonify({"error": "message required"}), 400
    result = get_user_agent(uid).invoke(
        {"messages": [("user", msg)]},
        config={"configurable": {"thread_id": f"user-{uid}"}, "recursion_limit": 12},
    )
    return jsonify({"answer": result["messages"][-1].content, "changed": _changed(result["messages"])})


@app.post("/chat/admin")
def chat_admin():
    msg = (request.get_json() or {}).get("message", "").strip()
    if not msg: return jsonify({"error": "message required"}), 400
    result = admin_agent.invoke(
        {"messages": [("user", msg)]},
        config={"configurable": {"thread_id": "admin"}, "recursion_limit": 12},
    )
    return jsonify({"answer": result["messages"][-1].content, "changed": _changed(result["messages"])})


# ─── 상담 (consultations) API ─────────────────────────────
@app.get("/api/consultations")
def api_consultations_list():
    """관리자: 현재 대기/활성 상담 목록"""
    return jsonify(db.list_consultations())


@app.get("/api/my-consultation")
def api_my_consultation():
    """사용자: 자기 진행 중인 상담 (없으면 null)"""
    uid = session.get("user_id")
    if not uid: return jsonify({"error": "로그인 필요"}), 401
    return jsonify(db.user_active_consultation(uid))


@app.post("/api/consultations/<int:cid>/accept")
def api_accept(cid):
    admin_id = request.args.get("admin", "admin-01")
    return jsonify(db.accept_consultation(cid, admin_id))


@app.post("/api/consultations/<int:cid>/close")
def api_close(cid):
    by = session.get("user_id") or request.args.get("admin", "admin")
    return jsonify(db.close_consultation(cid, by))


@app.post("/api/consultations/<int:cid>/messages")
def api_send_message(cid):
    body = request.get_json() or {}
    text = body.get("text", "").strip()
    sender = body.get("sender", "user")
    if not text: return jsonify({"error": "text required"}), 400
    return jsonify(db.add_message(cid, sender, text))


@app.get("/api/consultations/<int:cid>/messages")
def api_get_messages(cid):
    since = int(request.args.get("since", 0))
    return jsonify({
        "consultation": db.get_consultation(cid),
        "messages": db.list_messages(cid, since),
    })


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=6003)
