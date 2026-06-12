"""
데모 서버 공용 — 부팅 시 마켓플레이스에 '셀프 등록'한다.

서버가 뜨면(잠깐 기다렸다가) 레지스트리의 POST /api/servers 를 직접 호출한다.
→ seed 스크립트 없이도, 서버를 켜기만 하면 마켓플레이스에 나타난다(namespace=demo).
서버를 끄면 헬스 폴링이 OFFLINE 으로 내려준다(메타는 보존).
"""

import os
import threading
import time

import requests

# 레지스트리 주소(=마켓플레이스). 도커에선 서비스명으로 바꾼다. 예: http://marketplace:8000
REGISTRY = os.getenv("REGISTRY_URL", "http://localhost:8000")
# 레지스트리/게이트웨이가 '나'에게 접속할 때 쓸 호스트. 도커에선 이 서버의 서비스명.
SELF_HOST = os.getenv("SELF_HOST", "127.0.0.1")
# 등록은 '쓰기'라 공유 토큰이 필요(레지스트리가 MARKET_TOKEN 설정한 경우).
TOKEN = os.getenv("MARKET_TOKEN", "").strip()
_HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}


def self_register(server_id, name, port, owner="", description="", namespace="demo", delay=2.0):
    """백그라운드 스레드에서 잠시 후 레지스트리에 등록한다(서버가 뜬 뒤 등록되도록)."""
    endpoint = f"http://{SELF_HOST}:{port}/mcp"

    def _register():
        time.sleep(delay)
        try:
            r = requests.post(f"{REGISTRY}/api/servers", timeout=15, headers=_HEADERS, json={
                "id": server_id, "name": name, "endpoint": endpoint,
                "owner": owner, "namespace": namespace, "description": description,
            })
            tools = [t["name"] for t in r.json().get("tools", [])]
            print(f"[self-register] {server_id} → {REGISTRY}  tools={tools}")
        except Exception as e:
            print(f"[self-register] 실패({server_id}): {e}  — 레지스트리가 떠 있는지 확인하세요.")

    threading.Thread(target=_register, daemon=True).start()
