# travel_server.py — 가상 '여행사' MCP 서버
# 여행 상품 검색 / 예약 / 예약목록 도구를 제공한다. (예약은 메모리에 보관)
# 쇼핑몰과는 완전히 별개의 회사·프로세스 — 컨시어지 챗봇이 이 서버에도 동시에 붙는다.

import os
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("travel-agency")

TRIPS = {
    "제주도": {"price": 350000, "nights": 2},
    "도쿄": {"price": 700000, "nights": 3},
    "파리": {"price": 1800000, "nights": 5},
    "방콕": {"price": 600000, "nights": 4},
}

# stdio 라 도구 호출마다 새 프로세스 → 예약은 파일에 보관해야 누적된다.
_STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel_bookings.json")


def _load():
    return json.load(open(_STATE, encoding="utf-8")) if os.path.exists(_STATE) else []


def _save(bookings):
    json.dump(bookings, open(_STATE, "w", encoding="utf-8"), ensure_ascii=False)


@mcp.tool()
def search_trips(destination: str = "") -> str:
    """여행지로 상품을 검색한다 (빈 값이면 전체 목록)."""
    items = TRIPS if not destination else {k: v for k, v in TRIPS.items() if destination in k}
    if not items:
        return f"'{destination}' 상품 없음. 가능: {list(TRIPS)}"
    return "\n".join(f"{k}: {v['nights']}박 {v['price']:,}원" for k, v in items.items())


@mcp.tool()
def book_trip(destination: str, date: str = "미정") -> str:
    """여행을 예약한다. 예약번호를 발급한다."""
    if destination not in TRIPS:
        return f"{destination}: 취급하지 않음. 가능: {list(TRIPS)}"
    bookings = _load()
    bid = f"BK-{len(bookings) + 1:03d}"
    trip = TRIPS[destination]
    bookings.append({"id": bid, "dest": destination, "date": date, "price": trip["price"]})
    _save(bookings)
    return f"예약 완료! {bid} — {destination} {trip['nights']}박 ({date}) {trip['price']:,}원"


@mcp.tool()
def list_bookings() -> str:
    """내 여행 예약 목록을 보여준다."""
    bookings = _load()
    if not bookings:
        return "예약 내역 없음"
    return "\n".join(f"{b['id']}: {b['dest']} ({b['date']}) {b['price']:,}원" for b in bookings)


if __name__ == "__main__":
    mcp.run()
