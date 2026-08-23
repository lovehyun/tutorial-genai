# pip install mcp pydantic
#
# 도구 실패를 어떻게 알리나(isError) + 구조화된 성공 응답(structuredContent).
# 지금까지 도구는 전부 텍스트 하나만 돌려주는 "성공"만 다뤘다 — 실전에서는 "실패를 어떻게
# 알릴지"와 "구조화된 데이터를 어떻게 돌려줄지"가 똑같이 중요하다.

from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("error-structured-demo")


# [관전 포인트 1] 그냥 파이썬 예외를 raise 하면 FastMCP 가 자동으로 잡아서
#   CallToolResult(isError=True, content=[에러 메시지]) 로 감싸준다 — 프로토콜 레벨 에러가 아니라
#   "정상 응답인데 내용이 실패"라는 형태다(HTTP 로 치면 200 OK + {"error": "..."} 와 비슷한 결).
@mcp.tool()
def divide(a: float, b: float) -> float:
    """a를 b로 나눈다. b가 0이면 실패(isError=True)로 응답한다."""
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다.")
    return a / b


# [관전 포인트 2] 반환 타입을 Pydantic 모델로 명시하면 structuredContent 에 자동으로 채워진다.
#   플레인 dict(타입 힌트 없이)를 반환하면 이게 채워지지 않는다 — 타입힌트가 곧 스키마라는
#   1.basic 의 원칙이 여기서도 그대로 적용된다.
class WeatherResult(BaseModel):
    city: str
    temp_c: float
    condition: str


@mcp.tool()
def get_weather(city: str) -> WeatherResult:
    """가짜 날씨 데이터를 구조화된 형태로 돌려준다(데모용 하드코딩)."""
    return WeatherResult(city=city, temp_c=22.5, condition="맑음")


if __name__ == "__main__":
    mcp.run(transport="stdio")
