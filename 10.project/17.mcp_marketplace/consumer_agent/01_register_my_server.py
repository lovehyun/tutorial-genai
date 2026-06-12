"""
예제 ① 내 앱(MCP 서버)을 마켓플레이스에 '등록'하기.

  내 작은 MCP 서버를 띄우고  →  레지스트리(POST /api/servers)에 스스로 등록한다.
  등록 즉시 마켓플레이스가 list_tools 를 호출해 도구를 자동 수집한다.
  (서버를 끄면 헬스 폴링이 OFFLINE 으로 내려주고, 메타는 보존된다.)

실행:
  pip install mcp requests python-dotenv
  # 로컬 데모는 사설주소(127.0.0.1) 등록을 허용해야 한다 → 마켓을 ALLOW_PRIVATE_ENDPOINTS=1 로 띄울 것
  #   (run_demo.sh 는 이미 그렇게 띄운다)
  python 01_register_my_server.py            # 포트 8200 으로 'myteam-greet' 등록 후 계속 실행
  #  → 🖥️ MCP 서버 페이지에서 'myteam-greet' 가 ONLINE 으로 보이면 성공. Ctrl+C 로 종료.
"""

import os
import threading
import time

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

MARKET = os.getenv("MARKET_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("MARKET_TOKEN", "").strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

SERVER_ID = "myteam-greet"
PORT = int(os.getenv("PORT", "8200"))
# 레지스트리/게이트웨이가 '나'에게 접속할 주소. 같은 호스트면 127.0.0.1.
SELF_HOST = os.getenv("SELF_HOST", "127.0.0.1")

# ── 1) 평범한 MCP 서버 하나 ──────────────────────────────
mcp = FastMCP("My Greet MCP", host="0.0.0.0", port=PORT)


@mcp.tool()
def greet(name: str) -> str:
    """이름을 받아 인사한다."""
    return f"안녕하세요, {name}님! (myteam-greet 서버가 응답)"


@mcp.tool()
def shout(text: str) -> str:
    """받은 문장을 대문자로 외친다."""
    return text.upper() + "!!!"


# ── 2) 서버가 뜬 뒤(잠깐 대기) 마켓플레이스에 셀프 등록 ──
def register_later(delay: float = 2.0) -> None:
    def _register():
        time.sleep(delay)
        endpoint = f"http://{SELF_HOST}:{PORT}/mcp"
        try:
            r = requests.post(f"{MARKET}/api/servers", timeout=15, headers=HEADERS, json={
                "id": SERVER_ID, "name": "인사 서버", "owner": "내 팀",
                "namespace": "myteam", "endpoint": endpoint,
                "description": "이름을 받아 인사 / 문장을 외친다",
            })
            if r.ok:
                tools = [t["name"] for t in r.json().get("tools", [])]
                print(f"[register] 등록 성공: {SERVER_ID} → {MARKET}  수집된 도구={tools}")
            else:
                print(f"[register] 실패 {r.status_code}: {r.text[:200]}")
                print("  · 401 이면 MARKET_TOKEN 을, 'ENDPOINT_REJECTED' 면 "
                      "마켓을 ALLOW_PRIVATE_ENDPOINTS=1 로 띄웠는지 확인하세요.")
        except Exception as e:
            print(f"[register] 예외: {e}  — 마켓플레이스가 떠 있는지 확인하세요.")

    threading.Thread(target=_register, daemon=True).start()


if __name__ == "__main__":
    print(f"내 MCP 서버 기동: http://{SELF_HOST}:{PORT}/mcp  (Ctrl+C 종료)")
    register_later()
    mcp.run(transport="streamable-http")
