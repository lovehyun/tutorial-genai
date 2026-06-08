# shopping_server.py — 가상 '쇼핑몰' MCP 서버
# 상품 검색 / 할인 조회 / 주문 / 주문목록 도구를 제공한다. (재고·주문은 메모리에 보관)
# 별개 회사인 척하는 독립 프로세스 — 컨시어지 챗봇(app.py)이 이 서버에 붙어 쇼핑을 처리한다.

import os
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("shopping-mall")

CATALOG = {
    "노트북": {"price": 1200000, "stock": 5},
    "캐리어": {"price": 90000, "stock": 12},
    "헤드폰": {"price": 150000, "stock": 8},
    "카메라": {"price": 800000, "stock": 3},
}

# stdio 라 도구 호출마다 서버가 새 프로세스로 뜬다 → 주문은 파일에 보관해야 누적된다.
_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopping_orders.json")


def _load():
    return json.load(open(_STATE, encoding="utf-8")) if os.path.exists(_STATE) else []


def _save(orders):
    json.dump(orders, open(_STATE, "w", encoding="utf-8"), ensure_ascii=False)


@mcp.tool()
def search_products(query: str) -> str:
    """상품명을 검색해 가격·재고를 알려준다."""
    hits = {k: v for k, v in CATALOG.items() if query in k}
    if not hits:
        return f"'{query}' 검색 결과 없음. 취급 상품: {list(CATALOG)}"
    return "\n".join(f"{k}: {v['price']:,}원 (재고 {v['stock']})" for k, v in hits.items())


@mcp.tool()
def get_deal(product: str) -> str:
    """상품의 '할인 특가'를 알려준다 (정가의 10% 할인)."""
    if product not in CATALOG:
        return f"{product}: 취급하지 않음. 가능: {list(CATALOG)}"
    price = CATALOG[product]["price"]
    return f"{product} 특가: {int(price * 0.9):,}원 (정가 {price:,}원, 10% 할인)"


@mcp.tool()
def place_order(product: str, quantity: int = 1) -> str:
    """상품을 주문한다 (할인가 적용). 재고를 차감하고 주문번호를 발급한다."""
    if product not in CATALOG:
        return f"{product}: 취급하지 않음"
    item = CATALOG[product]
    if item["stock"] < quantity:
        return f"재고 부족: {product} 재고 {item['stock']}개"
    item["stock"] -= quantity
    orders = _load()
    oid = f"ORD-{len(orders) + 1:03d}"
    total = int(item["price"] * 0.9) * quantity
    orders.append({"id": oid, "product": product, "qty": quantity, "total": total})
    _save(orders)
    return f"주문 완료! {oid} — {product} x{quantity} = {total:,}원 (할인가)"


@mcp.tool()
def list_orders() -> str:
    """내 쇼핑몰 주문 목록을 보여준다."""
    orders = _load()
    if not orders:
        return "주문 내역 없음"
    return "\n".join(f"{o['id']}: {o['product']} x{o['qty']} = {o['total']:,}원" for o in orders)


if __name__ == "__main__":
    mcp.run()
