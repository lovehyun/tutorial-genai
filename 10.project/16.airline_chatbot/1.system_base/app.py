"""
항공 예약 시스템 #1 — 기본 시스템 (챗봇 없음).
이 예제: 사용자 뷰 / 관리자 뷰 두 페이지 + REST API. 추후 챗봇 레이어가 같은 API 활용.

사용자 뷰  (/)        : 항공편 검색 → 예약 / 내 예약 조회·취소
관리자 뷰  (/admin)   : 전체 예약 / 통계 / 항공편별 상세
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import db

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key")


# ─── 사용자 뷰 ─────────────────────────────────────────────
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


# ─── 관리자 뷰 ─────────────────────────────────────────────
@app.get("/admin")
def admin_view():
    return render_template("admin.html")


# ─── REST API (양쪽이 공유) ────────────────────────────────
@app.get("/api/flights")
def api_flights():
    return jsonify(db.search_flights(
        origin=request.args.get("origin"),
        dest=request.args.get("dest"),
    ))


@app.get("/api/my-bookings")
def api_my_bookings():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "로그인 필요"}), 401
    return jsonify(db.user_bookings(uid))


@app.post("/api/bookings")
def api_book():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"error": "로그인 필요"}), 401
    flight_id = (request.get_json() or {}).get("flight_id")
    if not flight_id:
        return jsonify({"error": "flight_id required"}), 400
    return jsonify(db.create_booking(uid, int(flight_id)))


@app.post("/api/bookings/<int:bid>/cancel")
def api_cancel(bid):
    actor = session.get("user_id") or "admin"
    return jsonify(db.cancel_booking(bid, actor))


# 관리자 전용
@app.get("/api/all-bookings")
def api_all_bookings():
    return jsonify(db.all_bookings())


@app.get("/api/stats")
def api_stats():
    return jsonify(db.stats())


@app.get("/api/bookings/<int:bid>/history")
def api_booking_history(bid):
    return jsonify(db.booking_history(bid))


if __name__ == "__main__":
    db.init_db()
    app.run(debug=True, port=6001)
