# shopping_server.py — [테스트 픽스처] '2조' 쇼핑몰 MCP 서버 (streamable-http, 포트 8003)

import os
from mcp.server.fastmcp import FastMCP
from _selfreg import self_register

PORT = 8003
mcp = FastMCP("shopping-mcp", host=os.getenv("MCP_HOST", "127.0.0.1"), port=PORT)

PRODUCTS = {
    "캐리어": 89000,
    "선크림": 12000,
    "보조배터리": 25000,
    "여행용 어댑터": 9000,
}
_ORDERS: list[dict] = []


@mcp.tool()
def search_products(keyword: str = "") -> str:
    """상품을 검색한다 (빈 값이면 전체 목록)."""
    items = PRODUCTS if not keyword else {k: v for k, v in PRODUCTS.items() if keyword in k}
    if not items:
        return f"'{keyword}' 상품 없음. 가능: {list(PRODUCTS)}"
    return "\n".join(f"{k}: {v:,}원" for k, v in items.items())


@mcp.tool()
def place_order(product: str, qty: int = 1) -> str:
    """상품을 주문하고 주문번호를 발급한다."""
    if product not in PRODUCTS:
        return f"{product}: 취급하지 않음. 가능: {list(PRODUCTS)}"
    oid = f"ORD-{len(_ORDERS) + 1:03d}"
    total = PRODUCTS[product] * qty
    _ORDERS.append({"id": oid, "product": product, "qty": qty, "total": total})
    return f"주문 완료! {oid} — {product} x{qty} = {total:,}원"


@mcp.tool()
def list_orders() -> str:
    """내 주문 목록을 보여준다."""
    if not _ORDERS:
        return "주문 내역 없음"
    return "\n".join(f"{o['id']}: {o['product']} x{o['qty']} {o['total']:,}원" for o in _ORDERS)


if __name__ == "__main__":
    self_register("shopping", "Shopping MCP", PORT, owner="2조", description="상품 검색/주문")
    print(f"Shopping MCP → http://127.0.0.1:{PORT}/mcp")
    mcp.run(transport="streamable-http")
