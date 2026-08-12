"""
5b/5c 라우팅 실습이 쓰는 지원 서버 — 이 파일 자체는 실습 대상이 아니다.
math_server.py 와 완전히 다른 도메인(시간/날씨)이라 "질의에 따라 다른 서버가 선택되는"
라우팅이 눈에 보인다.

원본: 8.mcp/2.openai/2.multi_tools/utility_server.py
"""

import logging
import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("UtilityServer")


@mcp.tool()
def current_time() -> str:
    """현재 시간을 반환합니다."""
    logging.info("current_time 호출됨")
    now = datetime.datetime.now()
    return f"현재 시간: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@mcp.tool()
def weather(city: str = "서울") -> str:
    """지정된 도시의 날씨 정보를 반환합니다 (가상 데이터)."""
    logging.info(f"weather 호출됨: city={city}")
    weather_data = {
        "서울": "맑음, 25도",
        "부산": "흐림, 28도",
        "대구": "비, 22도",
        "인천": "맑음, 24도",
    }
    weather_info = weather_data.get(city, "해당 도시의 날씨 정보는 없습니다.")
    return f"{city} 날씨: {weather_info}"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.info("유틸리티 서버 시작됨")
    logging.info("제공 기능: current_time, weather")
    mcp.run()
