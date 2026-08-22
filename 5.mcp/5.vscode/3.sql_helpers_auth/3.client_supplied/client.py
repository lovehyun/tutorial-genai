"""
케이스 3 데모 — '클라이언트'가 대상 DB 를 정한다. 같은 server.py 를 두 DB 로 붙여본다.

  1) shop.db 로 붙이기 → 쇼핑몰 테이블
  2) hr.db 로 붙이기   → 인사 테이블
같은 서버 코드, 자격증명 0. 어디에 붙을지는 '클라이언트가 세션에 준 CLIENT_DSN' 이 결정.

★ 접속정보는 StdioServerParameters(env=...) 로 넘긴다 — 도구 인자가 아니다(유출 방지).

실행:  python ../init_db.py  후  python client.py
"""

import asyncio
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SHOP = os.path.abspath(os.path.join(HERE, "..", "shop.db"))
HR = os.path.abspath(os.path.join(HERE, "..", "hr.db"))


async def call(s, name, **a):
    return (await s.call_tool(name, a)).content[0].text


async def use(label, dsn, sql):
    print(f"\n================ {label}  (CLIENT_DSN={dsn}) ================")
    # ★ 접속정보는 env 로 — 서버 자식 프로세스에만 전달, 도구 인자로는 절대 안 감
    params = StdioServerParameters(command="python", args=["server.py"],
                                   env={**os.environ, "CLIENT_DSN": dsn})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("which_db :", await call(s, "which_db"))
            print("결과:\n" + await call(s, "run_query", sql=sql))


async def main():
    await use("shop.db 로 붙이기", f"sqlite:{SHOP}",
              "SELECT name, price FROM products ORDER BY price DESC LIMIT 3")
    await use("hr.db 로 붙이기", f"sqlite:{HR}",
              "SELECT e.name, d.name AS dept FROM employees e JOIN departments d ON d.id=e.dept_id")


if __name__ == "__main__":
    asyncio.run(main())
