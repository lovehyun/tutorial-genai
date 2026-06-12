"""
consumer_agent/_market.py — 예제들이 공유하는 마켓플레이스 API 헬퍼(얇은 래퍼).

  · 조회(GET)는 토큰이 필요 없다.
  · 등록/구독/삭제 같은 '관리'와 게이트웨이 외 쓰기에는 공유 Bearer 토큰이 필요하다.
  · 주소·토큰은 환경변수로 받는다:  MARKET_URL, MARKET_TOKEN  (.env 도 지원)

이 파일은 02~04 예제가 import 한다. (01 register 예제는 자기 서버를 직접 띄우므로 단독 실행)
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

MARKET = os.getenv("MARKET_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("MARKET_TOKEN", "").strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}   # 관리 API에만 쓰임


def list_servers() -> list[dict]:
    """등록된 서버 목록(조회 — 토큰 불필요)."""
    return requests.get(f"{MARKET}/api/servers", timeout=10).json()


def ensure_consumer(consumer_id: str, name: str | None = None) -> None:
    """컨슈머를 만든다. POST 가 upsert 라 이미 있어도 안전(관리=토큰 필요)."""
    requests.post(f"{MARKET}/api/consumers", timeout=10, headers=HEADERS,
                  json={"id": consumer_id, "name": name or consumer_id})


def get_subscriptions(consumer_id: str) -> list[dict]:
    """이 컨슈머가 구독한 '서버 객체' 목록. (id 만 쓰려면 s['id'])"""
    r = requests.get(f"{MARKET}/api/consumers/{consumer_id}/subscriptions", timeout=10)
    return r.json() if r.ok else []


def set_subscriptions(consumer_id: str, server_ids: list[str]) -> None:
    """구독을 server_ids 로 '통째 교체'한다. []  를 주면 전체 해지."""
    requests.put(f"{MARKET}/api/consumers/{consumer_id}/subscriptions", timeout=10,
                 headers=HEADERS, json={"server_ids": server_ids})


def gateway_url(consumer_id: str) -> str:
    """이 컨슈머의 게이트웨이(MCP) 주소 — 여기에 붙으면 구독 서버 도구가 합쳐져 나온다."""
    return f"{MARKET}/mcp/consumers/{consumer_id}"
