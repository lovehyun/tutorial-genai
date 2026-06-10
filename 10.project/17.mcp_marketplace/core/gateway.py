"""
MCP 프록시 게이트웨이 (저수준 mcp.server.Server 기반).

소비자는 '팀 서버 주소'를 몰라도 된다. 게이트웨이 한 곳에만 붙으면,
게이트웨이가 구독한 서버들의 도구를 모아서 노출하고, 호출을 실제 서버로 중계한다.

두 가지 노출 형태 (둘 다 지원):
  · 통합   GET/POST  /mcp/consumers/<consumer_id>
           컨슈머가 구독한 모든 서버의 도구를 'serverid__tool' 로 네임스페이스해 한 묶음으로.
  · 개별   GET/POST  /mcp/servers/<server_id>
           특정 서버 하나만 프록시 (도구 이름 그대로).

설계 포인트
  · types.Tool(inputSchema=...) 로 업스트림 스키마를 '그대로' 미러링 → 인자 정보 보존.
  · list_tools/call_tool 는 매 요청마다 DB를 읽으므로, 구독·도구가 바뀌면 즉시 반영(캐시 staleness 없음).
  · OFFLINE/ARCHIVED 서버 호출은 업스트림에 가지 않고 즉시 SERVER_OFFLINE 로 응답.
  · 세션 매니저는 stateless + json_response → 프록시에 가장 단순한 형태.
"""

import json
import time
import asyncio
import logging
import contextlib

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

import db
from mcp_client import call_upstream

log = logging.getLogger("gateway")

NS = "__"          # 네임스페이스 구분자: travel__search_trips
DEAD = {"OFFLINE", "ARCHIVED"}

# 엔드포인트별 세션매니저 캐시. list_tools/call_tool 는 DB를 매번 읽으므로 캐시해도 안전.
_managers: dict[str, StreamableHTTPSessionManager] = {}
_lock = asyncio.Lock()
_stack: contextlib.AsyncExitStack | None = None


def set_exit_stack(stack: contextlib.AsyncExitStack) -> None:
    """앱 시작 시 호출 — 매니저들의 run() 컨텍스트를 여기에 보관(앱 종료까지 유지)."""
    global _stack
    _stack = stack


def _err(payload: dict) -> list[types.ContentBlock]:
    return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


def _text(content: list[types.ContentBlock]) -> str:
    """content 블록들에서 사람이 읽을 텍스트만 추려 합친다(로그 기록용)."""
    parts = []
    for b in content:
        t = getattr(b, "text", None)
        parts.append(t if t is not None else getattr(b, "type", "?"))
    return "\n".join(parts)


def _ip_of(server: Server) -> str:
    """현재 MCP 요청의 클라이언트 IP. nginx 뒤면 X-Forwarded-For 우선."""
    try:
        req = server.request_context.request          # streamable-http → Starlette Request
        xff = req.headers.get("x-forwarded-for")
        return xff.split(",")[0].strip() if xff else (req.client.host if req.client else "-")
    except Exception:
        return "-"


# ─── 서버 빌더 ─────────────────────────────────────────────
def _consumer_server(consumer_id: str) -> Server:
    """컨슈머의 구독 서버들을 네임스페이스로 합쳐 노출하는 저수준 MCP 서버."""
    server = Server(f"marketplace-consumer-{consumer_id}")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        out = []
        for s in db.get_subscriptions(consumer_id):           # 매 요청 DB 조회 → 항상 최신
            for t in s["tools"]:
                out.append(types.Tool(
                    name=f"{s['id']}{NS}{t['name']}",
                    description=f"[{s['name']}] {t['description']}",
                    inputSchema=t["input_schema"] or {"type": "object", "properties": {}},
                ))
        return out

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
        if NS not in name:
            return _err({"error": "BAD_TOOL_NAME", "detail": f"'serverid{NS}tool' 형식이어야 함", "name": name})
        sid, tool = name.split(NS, 1)
        subscribed = {s["id"] for s in db.get_subscriptions(consumer_id)}
        if sid not in subscribed:
            return _err({"error": "NOT_SUBSCRIBED", "server": sid, "consumer": consumer_id})
        return await _proxy(sid, tool, arguments, via=f"consumer:{consumer_id}", client_ip=_ip_of(server))

    return server


def _server_server(server_id: str) -> Server:
    """단일 서버만 프록시 (도구 이름 그대로)."""
    server = Server(f"marketplace-server-{server_id}")

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        s = db.get_server(server_id)
        if not s:
            return []
        return [types.Tool(
            name=t["name"], description=t["description"],
            inputSchema=t["input_schema"] or {"type": "object", "properties": {}},
        ) for t in s["tools"]]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
        return await _proxy(server_id, name, arguments, via=f"server:{server_id}", client_ip=_ip_of(server))

    return server


# ─── 중계 + 사용량 로그 + 장애 처리 ─────────────────────────
async def _proxy(server_id: str, tool: str, arguments: dict, via: str, client_ip: str = "-") -> list[types.ContentBlock]:
    t0 = time.perf_counter()
    s = db.get_server(server_id)
    if not s:
        db.record_call(server_id, tool, via, False, 0, "UNKNOWN_SERVER", arguments, "없는 서버", client_ip)
        return _err({"error": "UNKNOWN_SERVER", "server": server_id})
    if s["status"] in DEAD:                                    # 죽은 서버 → 업스트림 호출 안 함
        log.warning("BLOCK %s %s.%s status=%s", via, server_id, tool, s["status"])
        db.record_call(server_id, tool, via, False, 0, "SERVER_OFFLINE", arguments,
                       f"status={s['status']}", client_ip)
        return _err({"error": "SERVER_OFFLINE", "server": server_id, "status": s["status"]})
    try:
        log.info("PROXY %s(%s) -> %s.%s args=%s", via, client_ip, server_id, tool, arguments)
        content, is_error = await call_upstream(s["endpoint"], tool, arguments)
        db.record_call(server_id, tool, via, not is_error, (time.perf_counter() - t0) * 1000,
                       "TOOL_ERROR" if is_error else None, arguments, _text(content), client_ip)
        return content   # 도구 오류라도 content(에러 메시지)는 그대로 컨슈머에게 전달
    except Exception as e:                                     # 업스트림 통신 실패
        log.warning("FAIL %s %s.%s: %s", via, server_id, tool, e)
        db.record_call(server_id, tool, via, False, (time.perf_counter() - t0) * 1000,
                       "UPSTREAM_ERROR", arguments, str(e), client_ip)
        db.recompute_statuses()
        return _err({"error": "UPSTREAM_ERROR", "server": server_id, "detail": str(e)})


# ─── 세션 매니저 (엔드포인트별 캐시) ────────────────────────
async def _get_manager(key: str, build) -> StreamableHTTPSessionManager:
    async with _lock:
        mgr = _managers.get(key)
        if mgr is None:
            mgr = StreamableHTTPSessionManager(app=build(), stateless=False, json_response=True)
            await _stack.enter_async_context(mgr.run())        # 앱 종료까지 유지
            _managers[key] = mgr
        return mgr


# ─── ASGI 진입점 (main 에서 /mcp 아래에 마운트) ─────────────
async def gateway_asgi(scope, receive, send) -> None:
    if scope["type"] != "http":
        return
    # 게이트웨이(MCP streamable-http)는 토큰 불필요 — MCP 표준대로 개방.
    # (인증이 필요한 건 레지스트리 관리 API 와 채팅뿐이다. → app.py require_token)
    # 경로에서 'consumers'/'servers' 키워드를 찾고, 대상 id 는 '마지막 세그먼트'.
    #  · /mcp/consumers/<id>                 (통합)
    #  · /mcp/servers/<id>                   (개별 — 구버전)
    #  · /mcp/servers/<namespace>/<id>       (개별 — namespace 표시, id 가 유일하므로 라우팅 동일)
    #  (nginx prefix·root_path·마운트 방식에 무관하게 동작)
    segs = [p for p in scope["path"].split("/") if p]
    ident = segs[-1] if segs else ""
    kind = "consumers" if "consumers" in segs else ("servers" if "servers" in segs else "")
    if kind == "consumers":
        if not db.get_consumer(ident):
            return await _send_404(send, f"unknown consumer: {ident}")
        mgr = await _get_manager(f"c:{ident}", lambda: _consumer_server(ident))
    elif kind == "servers":
        if not db.get_server(ident):
            return await _send_404(send, f"unknown server: {ident}")
        mgr = await _get_manager(f"s:{ident}", lambda: _server_server(ident))
    else:
        return await _send_404(send, "use /mcp/consumers/<id> or /mcp/servers/<id>")
    await mgr.handle_request(scope, receive, send)


async def _send_404(send, msg: str) -> None:
    await send({"type": "http.response.start", "status": 404,
                "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body",
                "body": json.dumps({"error": msg}, ensure_ascii=False).encode()})
