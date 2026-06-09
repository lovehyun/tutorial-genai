"""
단일 ASGI 진입점 — 등록서버/UI(Flask) + MCP 프록시 게이트웨이를 한 프로세스로.

  /mcp/consumers/<id>  ┐
  /mcp/servers/<id>    ┘→ gateway (ASGI, MCP streamable-http 프록시)
  / , /api/* , /guide  → Flask (WSGI, 등록서버 + 마켓플레이스 UI + 가이드)

부가 기능
  · lifespan 에서 헬스 폴링 태스크 시작 — 주기적으로 모든 서버에 접속해 last_seen/도구 갱신.
  · AsyncExitStack 을 게이트웨이에 넘겨, 엔드포인트별 세션매니저 run() 을 앱 종료까지 유지.

실행 (개발)   : uvicorn main:app --port 8000   (core/ 안에서)
실행 (배포)   : uvicorn main:app --host 0.0.0.0 --port 8000 --root-path /mcp-market
              → nginx 가 https://gensapps.com/mcp-market/ 를 이 컨테이너로 프록시
"""

import os
import asyncio
import logging
import contextlib

# .env 로드(있으면) — OPENAI_API_KEY/ANTHROPIC_API_KEY 등을 다른 import 전에 채운다.
try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv(usecwd=True))
except Exception:
    pass

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware.wsgi import WSGIMiddleware

import db
import gateway
from app import flask_app
from mcp_client import probe_tools

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)            # 헬스 폴링 요청 로그 소음 제거
logging.getLogger("mcp.client.streamable_http").setLevel(logging.WARNING)
log = logging.getLogger("main")

POLL_SEC = int(os.getenv("HEALTH_POLL_SEC", "60"))   # 헬스 폴링 주기
PROBE_TIMEOUT = float(os.getenv("PROBE_TIMEOUT", "5"))


async def _poll_once() -> None:
    """모든 등록 서버에 접속해 살아있으면 last_seen/도구 갱신. 죽었으면 상태만 내려간다."""
    for s in db.all_endpoints():
        try:
            tools = await asyncio.wait_for(probe_tools(s["endpoint"]), timeout=PROBE_TIMEOUT)
            db.set_tools(s["id"], tools)
            db.mark_seen(s["id"])
        except Exception as e:
            log.info("health: %s 응답없음 (%s)", s["id"], type(e).__name__)
    db.recompute_statuses()


async def _health_loop() -> None:
    while True:
        try:
            await _poll_once()
        except Exception as e:
            log.warning("health loop 오류: %s", e)
        await asyncio.sleep(POLL_SEC)


@contextlib.asynccontextmanager
async def lifespan(app):
    db.init_db()
    async with contextlib.AsyncExitStack() as stack:
        gateway.set_exit_stack(stack)          # 게이트웨이 세션매니저들이 여기서 살아있음
        poller = asyncio.create_task(_health_loop())
        log.info("마켓플레이스 시작 — 헬스 폴링 %ds 주기", POLL_SEC)
        try:
            yield
        finally:
            poller.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await poller


app = Starlette(
    lifespan=lifespan,
    routes=[
        Mount("/mcp", app=gateway.gateway_asgi),       # 더 구체적인 경로 먼저
        Mount("/", app=WSGIMiddleware(flask_app)),     # 나머지는 Flask 로
    ],
)
