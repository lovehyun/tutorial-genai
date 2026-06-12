# weather_server.py — [테스트 픽스처] '3조' 날씨 MCP 서버 (streamable-http, 포트 8002)

import os
from mcp.server.fastmcp import FastMCP
from _selfreg import self_register

PORT = 8002
mcp = FastMCP("weather-mcp", host=os.getenv("MCP_HOST", "127.0.0.1"), port=PORT)

FORECAST = {
    "제주도": "맑음, 24℃",
    "도쿄": "흐림, 21℃",
    "파리": "비, 17℃",
    "방콕": "소나기, 32℃",
    "서울": "맑음, 23℃",
}


@mcp.tool()
def get_weather(city: str) -> str:
    """도시의 현재 날씨를 알려준다."""
    return f"{city}: {FORECAST.get(city, '예보 없음 (데모 데이터)')}"


@mcp.tool()
def pack_advice(city: str) -> str:
    """도시 날씨에 맞춰 챙길 물건을 추천한다."""
    w = FORECAST.get(city, "")
    if "비" in w or "소나기" in w:
        return f"{city}: 우산/우비를 챙기세요."
    if "맑음" in w:
        return f"{city}: 선크림/선글라스를 챙기세요."
    return f"{city}: 가벼운 겉옷을 챙기세요."


if __name__ == "__main__":
    self_register("weather", "Weather MCP", PORT, owner="3조", description="날씨 조회/준비물 추천")
    print(f"Weather MCP → http://127.0.0.1:{PORT}/mcp")
    mcp.run(transport="streamable-http")
