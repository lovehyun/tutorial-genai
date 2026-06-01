"""환율/주가 조회 — 트레이딩 봇 내부용 plain 함수 (도구가 아니라 단순 조회)."""

import requests


def usd_krw() -> float:
    """1 USD = ? KRW (무료 API, 키 불필요)."""
    r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
    return float(r.json()["rates"]["KRW"])


def stock_price(ticker: str):
    """yfinance 현재가 (USD). 실패 시 None."""
    import yfinance as yf

    d = yf.Ticker(ticker).history(period="1d")
    return None if d.empty else round(float(d["Close"].iloc[-1]), 2)
