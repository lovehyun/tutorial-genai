"""
항공 예약 시스템 #2 — 사용자 / 관리자 뷰에 각각 챗봇 / 에이전트 추가.
이 예제: #1 의 REST API 를 도구로 감싸, 각 뷰에서 자연어로 작업 가능하게.

#1 과의 차이:
  - 사용자 챗봇: 항공편 검색·예약·취소·내 예약 조회 (자기 자신에 한정)
  - 관리자 챗봇: 전체 예약·통계·히스토리 조회·강제 취소 (관리 권한)
  - 두 챗봇이 서로 다른 도구 세트 — 권한 분리 시연

다음 단계 (#3) 에서 "상담사 연결" 채팅이 더해짐.
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


# ─── 사용자용 도구 (자기 자신에 한정) ──────────────────────
def make_user_tools(user_id: str):
    """user_id 가 클로저로 묶인 도구 세트"""

    @tool
    def search_flights(origin: str | None = None, dest: str | None = None) -> list[dict]:
        """항공편을 검색한다. origin/dest 는 공항코드(예: ICN, NRT). 둘 다 비우면 전체."""
        return db.search_flights(origin, dest)

    @tool
    def book_flight(flight_id: int) -> dict:
        """flight_id 의 항공편을 현재 사용자 이름으로 예약한다."""
        return db.create_booking(user_id, flight_id)

    @tool
    def my_bookings() -> list[dict]:
        """현재 사용자의 모든 예약을 반환."""
        return db.user_bookings(user_id)

    @tool
    def cancel_my_booking(booking_id: int) -> dict:
        """현재 사용자의 예약을 취소한다 (자기 것만)."""
        # 권한 체크 — 자기 예약인지 확인
        bookings = db.user_bookings(user_id)
        if booking_id not in {b["id"] for b in bookings}:
            return {"error": "해당 예약은 본인 것이 아닙니다"}
        return db.cancel_booking(booking_id, actor=user_id)

    return [search_flights, book_flight, my_bookings, cancel_my_booking]


USER_PROMPT = """\
당신은 항공 예약 비서입니다. 사용자의 자연어 명령을 적절한 도구로 변환해 처리합니다.

도구:
- search_flights(origin, dest)  : 항공편 검색
- book_flight(flight_id)        : 예약
- my_bookings()                 : 내 예약 조회
- cancel_my_booking(booking_id) : 내 예약 취소

원칙:
- 변경(예약/취소) 전에는 정확한 id 가 필요하니, 모호하면 먼저 검색/조회로 id 확인
- 한 작업당 도구 호출 2~3회를 넘기지 말 것
- 결과는 한국어로 간결히 1~3문장
- "어떤 항공편 ID 인지 모르겠으면" 사용자에게 명시적으로 물어보기
"""


# ─── 관리자용 도구 (전체 시스템 접근) ──────────────────────
@tool
def admin_all_bookings() -> list[dict]:
    """관리자: 전체 예약 목록."""
    return db.all_bookings()


@tool
def admin_stats() -> dict:
    """관리자: 시스템 통계 (총 항공편/예약/취소)."""
    return db.stats()


@tool
def admin_booking_history(booking_id: int) -> list[dict]:
    """관리자: 특정 예약의 상태 변경 이력."""
    return db.booking_history(booking_id)


@tool
def admin_force_cancel(booking_id: int) -> dict:
    """관리자: 임의 예약을 강제 취소 (actor='admin')."""
    return db.cancel_booking(booking_id, actor="admin")


ADMIN_TOOLS = [admin_all_bookings, admin_stats, admin_booking_history, admin_force_cancel]
ADMIN_PROMPT = """\
당신은 항공사 운영 관리자를 보조하는 비서입니다.

도구:
- admin_stats()                 : 시스템 통계
- admin_all_bookings()          : 전체 예약 목록
- admin_booking_history(id)     : 예약 이력
- admin_force_cancel(id)        : 강제 취소

원칙:
- 변경(강제 취소) 전에는 반드시 booking_id 와 사유를 확인
- 통계 질문은 admin_stats 한 번 호출로 충분
- 한국어, 간결하게
"""

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
admin_checkpointer = MemorySaver()
admin_agent = create_react_agent(
    llm, ADMIN_TOOLS, prompt=ADMIN_PROMPT, checkpointer=admin_checkpointer,
)


# 사용자 에이전트는 user_id 별로 캐시 (도구가 user_id 에 묶여 있음)
USER_AGENTS: dict[str, object] = {}
USER_CHECKPOINTERS: dict[str, MemorySaver] = {}


def get_user_agent(user_id: str):
    if user_id not in USER_AGENTS:
        cp = MemorySaver()
        USER_CHECKPOINTERS[user_id] = cp
        USER_AGENTS[user_id] = create_react_agent(
            llm, make_user_tools(user_id), prompt=USER_PROMPT, checkpointer=cp,
        )
    return USER_AGENTS[user_id]


# ─── 화면 ─────────────────────────────────────────────────
@app.get("/")
def user_view():
    if "user_id" not in session:
        return render_template("login.html")
    return render_template("user.html", user_id=session["user_id"])


@app.post("/login")
def login():
    uid = request.form.get("user_id", "").strip()
    if uid:
        session["user_id"] = uid
    return redirect(url_for("user_view"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("user_view"))


@app.get("/admin")
def admin_view():
    return render_template("admin.html")


# ─── REST API (1단계와 동일) ───────────────────────────────
@app.get("/api/flights")
def api_flights():
    return jsonify(db.search_flights(
        origin=request.args.get("origin"), dest=request.args.get("dest")))


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
    if not flight_id: return jsonify({"error": "flight_id required"}), 400
    return jsonify(db.create_booking(uid, int(flight_id)))


@app.post("/api/bookings/<int:bid>/cancel")
def api_cancel(bid):
    actor = session.get("user_id") or "admin"
    return jsonify(db.cancel_booking(bid, actor))


@app.get("/api/all-bookings")
def api_all_bookings(): return jsonify(db.all_bookings())


@app.get("/api/stats")
def api_stats(): return jsonify(db.stats())


@app.get("/api/bookings/<int:bid>/history")
def api_booking_history(bid): return jsonify(db.booking_history(bid))


# ─── 챗봇 라우트 (각 뷰별로 다른 도구) ─────────────────────
WRITE_TOOL_NAMES = {"book_flight", "cancel_my_booking", "admin_force_cancel"}


def _detect_change(messages):
    for m in messages:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                if c["name"] in WRITE_TOOL_NAMES:
                    return True
    return False


@app.post("/chat/user")
def chat_user():
    uid = session.get("user_id")
    if not uid: return jsonify({"error": "로그인 필요"}), 401
    msg = (request.get_json() or {}).get("message", "").strip()
    if not msg: return jsonify({"error": "message required"}), 400

    agent = get_user_agent(uid)
    result = agent.invoke(
        {"messages": [("user", msg)]},
        config={"configurable": {"thread_id": f"user-{uid}"}, "recursion_limit": 12},
    )
    return jsonify({
        "answer":  result["messages"][-1].content,
        "changed": _detect_change(result["messages"]),
    })


@app.post("/chat/admin")
def chat_admin():
    msg = (request.get_json() or {}).get("message", "").strip()
    if not msg: return jsonify({"error": "message required"}), 400

    result = admin_agent.invoke(
        {"messages": [("user", msg)]},
        config={"configurable": {"thread_id": "admin"}, "recursion_limit": 12},
    )
    return jsonify({
        "answer":  result["messages"][-1].content,
        "changed": _detect_change(result["messages"]),
    })


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=6002)
