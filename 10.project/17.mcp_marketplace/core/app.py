"""
등록 서버(Registry) + 마켓플레이스 UI + 멘티용 SDK 가이드 (Flask, WSGI).

main.py 가 이 Flask 앱과 게이트웨이(ASGI)를 한 ASGI 프로세스로 합쳐 실행한다.
nginx 가 앞에 prefix(예: /mcp-market)를 붙여도, ProxyFix + 상대경로로 그대로 동작한다.

엔드포인트
  GET  /                                   마켓플레이스 UI (검색/탐색/구독)
  GET  /guide                              멘티용 SDK 가이드 문서
  GET  /api/servers                        서버 목록
  POST /api/servers                        서버 등록(+도구 자동수집)   ← 셀프등록도 이걸 호출
  POST /api/servers/<id>/refresh           도구 재수집
  DELETE /api/servers/<id>
  POST /heartbeat   {server_id}            서버 생존 신고(선택) — last_seen 갱신
  GET  /api/consumers / POST / DELETE
  GET/PUT /api/consumers/<id>/subscriptions
  GET  /api/health                         상태 재계산 후 요약
"""

import asyncio
from functools import wraps

from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

import db
import gateway
import security
import chat
from mcp_client import probe_tools

flask_app = Flask(__name__)
# nginx reverse proxy 의 X-Forwarded-* (Host/Proto/Prefix) 신뢰 → url_for/script_root 가 prefix 반영
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
db.init_db()


def require_token(f):
    """이 라우트에만 공유 Bearer 토큰을 요구한다.
       적용: 레지스트리 관리(서버/컨슈머/구독 변경) + 채팅(LLM 비용 발생).
       미적용(개방): 모든 읽기, 게이트웨이 /mcp/*(MCP 표준), 도구 테스트 호출."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not security.token_ok(request.headers.get("Authorization")):
            return jsonify({"error": "UNAUTHORIZED", "detail": "Bearer 토큰이 필요합니다"}), 401
        return f(*args, **kwargs)
    return wrapper


def _probe_and_store(server_id: str, endpoint: str) -> bool:
    """서버에 접속해 도구 수집 + 생존표시. 실패해도 등록 자체는 막지 않는다."""
    try:
        tools = asyncio.run(probe_tools(endpoint))
        db.set_tools(server_id, tools)
        db.mark_seen(server_id)
        return True
    except Exception as e:
        flask_app.logger.warning("probe 실패 %s (%s): %s", server_id, endpoint, e)
        db.recompute_statuses()
        return False


# ─── 페이지 ────────────────────────────────────────────────
@flask_app.get("/")
def dashboard():
    return render_template("dashboard.html", base=request.script_root, active="dashboard")


@flask_app.get("/browse")
def browse():
    return render_template("browse.html", base=request.script_root, active="browse")


@flask_app.get("/consumers")
def consumers_page():
    return render_template("consumers.html", base=request.script_root, active="consumers")


@flask_app.get("/playground")
def playground():
    return render_template("playground.html", base=request.script_root, active="playground")


@flask_app.get("/logs")
def logs():
    return render_template("logs.html", base=request.script_root, active="logs")


@flask_app.get("/chat")
def chat_page():
    return render_template("chat.html", base=request.script_root, active="chat")


@flask_app.get("/guide")
def guide():
    # 공개 베이스 URL(프리픽스 포함) — 멘티가 그대로 복붙할 수 있게 실제 주소로 렌더
    public = request.host_url.rstrip("/") + request.script_root
    return render_template("guide.html", base=request.script_root, public=public, active="guide")


# ─── 통계 / 로그 API ───────────────────────────────────────
@flask_app.get("/api/stats")
def api_stats():
    db.recompute_statuses()
    return jsonify(db.stats())


@flask_app.get("/api/calls")
def api_calls():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 20, type=int)
    return jsonify(db.list_calls(page, size))


@flask_app.get("/api/token-hint")
def api_token_hint():
    """UI 편의용 — SHOW_TOKEN_IN_UI=1 일 때만 토큰을 알려준다(데모). 아니면 null."""
    return jsonify({"token": security.token_hint(), "auth": security.auth_enabled()})


@flask_app.get("/api/llm")
def api_llm():
    """채팅에 쓸 수 있는 LLM provider 목록 + 기본값 (키 설정 여부 기준). 읽기 공개."""
    return jsonify({"available": chat.available(), "default": chat.provider()})


@flask_app.post("/api/chat")
@require_token
def api_chat():
    """채팅 컨슈머 — 선택 도구만 노출해 tool-calling. 호출은 게이트웨이 프록시로 실행(로그에 기록)."""
    body = request.get_json(force=True, silent=True) or {}
    cid = body.get("consumer_id")
    if not cid:
        return jsonify({"error": "'consumer_id' 필수"}), 400
    result = asyncio.run(chat.run_chat(
        cid, body.get("messages", []), body.get("enabled_tools"),
        ip=request.remote_addr or "-", prov=body.get("provider"),
    ))
    return jsonify(result)


# ─── 서버(SERVER) API ──────────────────────────────────────
@flask_app.get("/api/servers")
def api_list_servers():
    return jsonify(db.list_servers())


@flask_app.get("/api/servers/<server_id>")
def api_get_server(server_id):
    s = db.get_server(server_id)
    return (jsonify(s), 200) if s else (jsonify({"error": "없는 서버"}), 404)


@flask_app.post("/api/servers")
@require_token
def api_register_server():
    body = request.get_json(force=True, silent=True) or {}
    for f in ("id", "name", "endpoint"):
        if not body.get(f):
            return jsonify({"error": f"'{f}' 필수"}), 400
    reason = security.check_endpoint(body["endpoint"])      # SSRF 방어
    if reason:
        return jsonify({"error": "ENDPOINT_REJECTED", "detail": reason}), 400
    db.upsert_server(
        id=body["id"], name=body["name"], endpoint=body["endpoint"],
        owner=body.get("owner", ""), namespace=body.get("namespace", "default"),
        description=body.get("description", ""),
    )
    _probe_and_store(body["id"], body["endpoint"])
    return jsonify(db.get_server(body["id"])), 201


@flask_app.post("/api/servers/<server_id>/refresh")
@require_token
def api_refresh_server(server_id):
    s = db.get_server(server_id)
    if not s:
        return jsonify({"error": "없는 서버"}), 404
    _probe_and_store(server_id, s["endpoint"])
    return jsonify(db.get_server(server_id))


@flask_app.delete("/api/servers/<server_id>")
@require_token
def api_delete_server(server_id):
    db.delete_server(server_id)
    return jsonify({"ok": True})


def _blocks_to_text(blocks) -> str:
    """MCP content 블록 → 화면에 보여줄 텍스트."""
    out = []
    for b in blocks:
        t = getattr(b, "text", None)
        out.append(t if t is not None else repr(b))
    return "\n".join(out)


@flask_app.post("/api/servers/<server_id>/call")
def api_call_tool(server_id):
    """UI '도구 실행(try it)' — 게이트웨이 프록시 경로를 그대로 타서 도구를 호출한다.
       (DEAD 체크·에러처리는 gateway._proxy 가 담당. LLM 없이 바로 결과 확인용.)"""
    if not db.get_server(server_id):
        return jsonify({"error": "없는 서버"}), 404
    body = request.get_json(force=True, silent=True) or {}
    tool = body.get("tool")
    if not tool:
        return jsonify({"error": "'tool' 필수"}), 400
    # ProxyFix 가 X-Forwarded-For 를 remote_addr 로 반영 → 실제 클라이언트 IP
    blocks = asyncio.run(gateway._proxy(server_id, tool, body.get("arguments") or {},
                                        via="ui", client_ip=request.remote_addr or "-"))
    return jsonify({"result": _blocks_to_text(blocks)})


@flask_app.post("/heartbeat")
@require_token
def heartbeat():
    """서버가 살아있다고 직접 신고(선택적). 레지스트리 폴링과 병행 가능."""
    body = request.get_json(force=True, silent=True) or {}
    sid = body.get("server_id")
    if not sid or not db.get_server(sid):
        return jsonify({"error": "등록되지 않은 server_id"}), 400
    db.mark_seen(sid)
    return jsonify({"ok": True, "server_id": sid})


# ─── 컨슈머(CONSUMER) API ──────────────────────────────────
@flask_app.get("/api/consumers")
def api_list_consumers():
    return jsonify(db.list_consumers())


@flask_app.post("/api/consumers")
@require_token
def api_register_consumer():
    body = request.get_json(force=True, silent=True) or {}
    for f in ("id", "name"):
        if not body.get(f):
            return jsonify({"error": f"'{f}' 필수"}), 400
    db.upsert_consumer(id=body["id"], name=body["name"], owner=body.get("owner", ""))
    return jsonify(db.get_consumer(body["id"])), 201


@flask_app.delete("/api/consumers/<consumer_id>")
@require_token
def api_delete_consumer(consumer_id):
    db.delete_consumer(consumer_id)
    return jsonify({"ok": True})


# ─── 구독(SUBSCRIPTION) API ────────────────────────────────
@flask_app.get("/api/consumers/<consumer_id>/subscriptions")
def api_get_subscriptions(consumer_id):
    if not db.get_consumer(consumer_id):
        return jsonify({"error": "없는 컨슈머"}), 404
    return jsonify(db.get_subscriptions(consumer_id))


@flask_app.put("/api/consumers/<consumer_id>/subscriptions")
@require_token
def api_set_subscriptions(consumer_id):
    if not db.get_consumer(consumer_id):
        return jsonify({"error": "없는 컨슈머"}), 404
    body = request.get_json(force=True, silent=True) or {}
    db.set_subscriptions(consumer_id, body.get("server_ids", []))
    return jsonify(db.get_subscriptions(consumer_id))


# ─── 헬스 요약 ─────────────────────────────────────────────
@flask_app.get("/api/health")
def api_health():
    db.recompute_statuses()
    servers = db.list_servers()
    summary = {}
    for s in servers:
        summary[s["status"]] = summary.get(s["status"], 0) + 1
    return jsonify({"summary": summary, "servers": [
        {"id": s["id"], "status": s["status"], "last_seen": s["last_seen"]} for s in servers
    ]})


if __name__ == "__main__":
    # 게이트웨이 없이 등록서버/UI 만 단독 실행할 때(개발용). 정식 실행은 main.py.
    flask_app.run(port=5070, debug=True)
