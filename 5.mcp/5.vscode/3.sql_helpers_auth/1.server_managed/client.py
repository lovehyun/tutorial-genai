"""
케이스 1 데모 클라이언트 — 그냥 붙어서 쓴다(신원 제시 없음).
서버가 .env 자격증명으로 DB 에 로그인하고, 결과만 돌려준다.

실행:  python ../init_db.py  후  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.stdout.reconfigure(encoding="utf-8")


async def call(s, name, **a):
    return (await s.call_tool(name, a)).content[0].text


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print("── 테이블 목록 ──")
            print(await call(s, "list_tables"))
            print("\n── 고객별 결제액(조인+집계) ──")
            print(await call(s, "run_query", sql="""
                SELECT c.name, SUM(oi.quantity*oi.unit_price) AS 결제액
                FROM customers c JOIN orders o ON o.customer_id=c.id
                JOIN order_items oi ON oi.order_id=o.id
                GROUP BY c.id ORDER BY 결제액 DESC
            """))


if __name__ == "__main__":
    asyncio.run(main())
