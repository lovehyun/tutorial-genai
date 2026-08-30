# server2.py — 기본 유틸 도구(날짜/시간) + 외부 API 호출 도구(주가 조회)가 섞인 MCP 서버
# pip install yfinance
#
# server.py 와 마찬가지로 서버는 아무 것도 막지 않는다 — get_stock_price 도 부르면 그냥
# 실제로 인터넷에 나가서 실시간 데이터를 받아온다. get_date/get_time 은 완전히 안전하지만
# get_stock_price 는 "외부로 나가는 호출"이라 5.total_hitl.py 에서 위험군으로 분류한다.
#
# 실행: 클라이언트가 stdio 로 자동 실행하므로 직접 띄울 필요 없다.

from datetime import datetime

import yfinance as yf
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("UtilServer")


# ── 안전한 도구 (외부 호출 없음, 완전히 결정적이진 않지만 부작용 없음) ──

@mcp.tool()
def get_date() -> str:
    """오늘 날짜를 돌려준다."""
    return datetime.now().strftime("%Y-%m-%d")


@mcp.tool()
def get_time() -> str:
    """지금 시각을 돌려준다."""
    return datetime.now().strftime("%H:%M:%S")


# ── 위험한 도구 (외부 API 호출 — 네트워크로 나간다) ──

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """지정한 종목의 현재가를 조회한다 (yfinance).

    Args:
        ticker: 종목 코드. 미국 주식은 'AAPL'/'TSLA' 처럼, 한국 주식은
                '005930.KS'(삼성전자)처럼 거래소 접미사를 붙인다.
    """
    info = yf.Ticker(ticker).fast_info
    price = info.get("lastPrice")
    currency = info.get("currency", "")
    if price is None:
        return f"'{ticker}' 종목 정보를 찾을 수 없습니다."
    return f"{ticker} 현재가: {price} {currency}"


if __name__ == "__main__":
    mcp.run()   # stdio — 클라이언트가 자식 프로세스로 띄운다
