"""
sql-helper 데모 클라이언트 — 실제 클라이언트(Claude Code 등) 없이도 서버를 확인한다.

LLM 이 하는 일(스키마 파악 → SQL 작성 → 실행)을 '손으로' 흉내낸다:
  1) list_tables / describe_table 로 구조 확인
  2) 조인·집계 SQL 을 run_query 로 실행
  3) 읽기 전용 가드가 쓰기 쿼리를 막는지 확인

실행:
  python init_db.py     # 먼저 샘플 DB 생성
  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Windows 콘솔(cp949)에서도 한글 표 출력이 깨지지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")


async def call(session, name, **args):
    r = await session.call_tool(name, args)
    return r.content[0].text


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("── 1) 테이블 목록 ──")
            print(await call(session, "list_tables"))

            print("\n── 2) orders 구조 ──")
            print(await call(session, "describe_table", table="orders"))

            print("\n── 3) 조인+집계: 도시별 총 매출 (취소 주문 제외) ──")
            sql = """
                SELECT c.city,
                       COUNT(DISTINCT o.id)              AS 주문수,
                       SUM(oi.quantity * oi.unit_price)  AS 총매출
                FROM customers c
                JOIN orders o       ON o.customer_id = c.id
                JOIN order_items oi ON oi.order_id = o.id
                WHERE o.status <> 'cancelled'
                GROUP BY c.city
                ORDER BY 총매출 DESC
            """
            print(await call(session, "run_query", sql=sql))

            print("\n── 4) 조인: 가장 많이 팔린 상품 TOP 3 ──")
            sql2 = """
                SELECT p.name, SUM(oi.quantity) AS 판매수량
                FROM order_items oi
                JOIN orders o   ON o.id = oi.order_id
                JOIN products p ON p.id = oi.product_id
                WHERE o.status <> 'cancelled'
                GROUP BY p.id
                ORDER BY 판매수량 DESC
                LIMIT 3
            """
            print(await call(session, "run_query", sql=sql2))

            print("\n── 5) 읽기 전용 가드 확인: DELETE 시도 (거부돼야 정상) ──")
            print(await call(session, "run_query", sql="DELETE FROM customers"))


if __name__ == "__main__":
    asyncio.run(main())
