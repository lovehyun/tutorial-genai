"""
케이스 2 데모 — 같은 서버에 '두 사용자'가 서로 다른 토큰으로 붙어, 다른 범위를 받는다.

  analyst(tok-analyst): customers(PII) 못 봄 → 조회 시도하면 거부
  admin(tok-admin)    : 전체 접근
  무토큰/오토큰        : 401 (미들웨어 authN)

실행: (터미널1) python server.py    (터미널2) python client.py
"""

import asyncio
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

sys.stdout.reconfigure(encoding="utf-8")

# ── 데모(로컬)는 평문 http. 실제 배포는 아래 https 로 바꾼다 (둘은 공존 불가) ──
URL = "http://localhost:8000/mcp"
# URL = "https://api.example.com/mcp"     # ← 배포 시. 나머지 코드는 그대로.

# ── (배포용, 주석) 사설 CA / mTLS 가 필요할 때만: TLS 커스텀 httpx 클라이언트 ──
# 정식 인증서(Let's Encrypt 등)면 이 팩토리 없이 URL 만 https 로 바꾸면 된다(자동 검증).
# import httpx
# def tls_factory(headers=None, timeout=None, auth=None):
#     return httpx.AsyncClient(
#         headers=headers, timeout=timeout, auth=auth, follow_redirects=True,
#         verify="/etc/ssl/company-ca.pem",     # ① 사설/사내 CA 로 검증
#         # verify=False,                         # ② (개발용만!) 검증 끔 — 운영 금지(MITM)
#         # cert=("client.crt", "client.key"),   # ③ mTLS: 클라 인증서도 제시
#     )


def _root(e):
    while isinstance(e, BaseExceptionGroup) and e.exceptions:
        e = e.exceptions[0]
    return e


async def call(s, name, **a):
    return (await s.call_tool(name, a)).content[0].text


async def session_for(token):
    headers = {"Authorization": f"Bearer {token}"} if token else None
    return streamablehttp_client(URL, headers=headers)
    # 사설 CA/mTLS 배포 시 ↓ (위 tls_factory 주석 해제 후):
    # return streamablehttp_client(URL, headers=headers, httpx_client_factory=tls_factory)


async def run_as(label, token):
    print(f"\n================ {label} (token={token!r}) ================")
    try:
        async with await session_for(token) as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                print("whoami     :", await call(s, "whoami"))  # 시스템콜이 아닌 mcp 함수콜
                print("list_tables:\n" + await call(s, "list_tables"))
                print("products 조회:\n" + await call(s, "run_query", sql="SELECT name, price FROM products ORDER BY price DESC"))
                print("customers(PII) 조회:\n" + await call(s, "run_query", sql="SELECT name, email FROM customers"))
    except Exception as e:
        print("  접속 거부:", type(_root(e)).__name__, _root(e))


async def main():
    await run_as("analyst", "tok-analyst")   # customers 거부 예상
    await run_as("admin", "tok-admin")       # 전체 허용
    await run_as("무토큰", None)              # 401 예상


if __name__ == "__main__":
    asyncio.run(main())
