import logging
import datetime
from mcp.server.fastmcp import FastMCP

# 유틸리티 기능을 제공하는 서버
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
    
    # 가상 날씨 데이터
    weather_data = {
        "서울": "맑음, 25도",
        "부산": "흐림, 28도", 
        "대구": "비, 22도",
        "인천": "맑음, 24도"
    }
    
    weather_info = weather_data.get(city, "해당 도시의 날씨 정보는 없습니다.")
    return f"{city} 날씨: {weather_info}"

if __name__ == "__main__":
    # 로깅 설정: 시간, 레벨, 메시지를 포함하여 stderr에 출력
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    logging.info("유틸리티 서버 시작됨")
    logging.info("제공 기능: current_time, weather")

    mcp.run()


# CLI stdin 테스트
# 1단계 - 초기화 요청:
# {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}
# 2단계 - initialized 알림 (중요!):
# {"jsonrpc": "2.0", "method": "notifications/initialized"}
# 3단계 - 이제 도구 목록 조회:
# {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
# 4단계 - 도구 호출:
# {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "hello", "arguments": {"name": "Alice"}}}
