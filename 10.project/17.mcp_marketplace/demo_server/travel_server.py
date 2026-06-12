# travel_server.py — [테스트 픽스처] '1조' 여행사 MCP 서버 (streamable-http, 포트 8001)
#
# 우리 서비스(등록서버+게이트웨이)를 테스트하기 위한 더미 서버.
# 부팅하면 _selfreg 로 마켓플레이스에 자동 등록된다(namespace=demo).

import os
from mcp.server.fastmcp import FastMCP
from _selfreg import self_register

PORT = 8001
mcp = FastMCP("travel-mcp", host=os.getenv("MCP_HOST", "127.0.0.1"), port=PORT)

TRIPS = {
    "제주도": {"price": 350000, "nights": 2},
    "도쿄": {"price": 700000, "nights": 3},
    "파리": {"price": 1800000, "nights": 5},
    "방콕": {"price": 600000, "nights": 4},
}
_BOOKINGS: list[dict] = []


@mcp.tool()
def search_trips(destination: str = "") -> str:
    """여행지로 상품을 검색한다 (빈 값이면 전체 목록)."""
    items = TRIPS if not destination else {k: v for k, v in TRIPS.items() if destination in k}
    if not items:
        return f"'{destination}' 상품 없음. 가능: {list(TRIPS)}"
    return "\n".join(f"{k}: {v['nights']}박 {v['price']:,}원" for k, v in items.items())


@mcp.tool()
def book_trip(destination: str, date: str = "미정") -> str:
    """여행을 예약하고 예약번호를 발급한다."""
    if destination not in TRIPS:
        return f"{destination}: 취급하지 않음. 가능: {list(TRIPS)}"
    bid = f"BK-{len(_BOOKINGS) + 1:03d}"
    trip = TRIPS[destination]
    _BOOKINGS.append({"id": bid, "dest": destination, "date": date, "price": trip["price"]})
    return f"예약 완료! {bid} — {destination} {trip['nights']}박 ({date}) {trip['price']:,}원"


@mcp.tool()
def list_bookings() -> str:
    """내 여행 예약 목록을 보여준다."""
    if not _BOOKINGS:
        return "예약 내역 없음"
    return "\n".join(f"{b['id']}: {b['dest']} ({b['date']}) {b['price']:,}원" for b in _BOOKINGS)


if __name__ == "__main__":
    self_register("travel", "Travel MCP", PORT, owner="1조", description="여행 상품 검색/예약")
    print(f"Travel MCP → http://127.0.0.1:{PORT}/mcp")
    mcp.run(transport="streamable-http")
