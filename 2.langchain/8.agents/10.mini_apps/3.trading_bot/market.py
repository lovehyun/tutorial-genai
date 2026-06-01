"""
환율/주가 조회 — 트레이딩 봇 내부용 plain 함수 (도구가 아니라 단순 조회).

두 가지 소스를 모두 지원:
  (기본) 실제 API  — open.er-api.com(환율) / yfinance(주가)
  (선택) 데모 서버 — demo_market_server.py (매초 랜덤 변동, 키 불필요·빠른 데모용)

전환 방법: .env 에 DEMO_MARKET_URL 설정 시 데모 서버로 분기, 없으면 실제 API.
  DEMO_MARKET_URL=http://localhost:5002
"""

import os
import requests

# 데모 시세 서버 URL (설정 시 실제 API 대신 이 서버 조회). 미설정이면 실제 API 사용.
DEMO_MARKET_URL = os.getenv("DEMO_MARKET_URL")  # 예: "http://localhost:5002"


def usd_krw() -> float:
    """1 USD = ? KRW."""
    if DEMO_MARKET_URL:                       # ── 데모 서버 ──
        r = requests.get(f"{DEMO_MARKET_URL}/api/exchange",
                         params={"base": "USD", "target": "KRW"}, timeout=10)
        return float(r.json()["rate"])
    # ── 실제 API (기본, 무료·키 불필요) ──
    r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
    return float(r.json()["rates"]["KRW"])


def stock_price(ticker: str):
    """현재가 (USD). 실패 시 None."""
    if DEMO_MARKET_URL:                       # ── 데모 서버 ──
        r = requests.get(f"{DEMO_MARKET_URL}/api/stock/{ticker}", timeout=10)
        return round(float(r.json()["price"]), 2)
    # ── 실제 API (기본): yfinance ──
    import yfinance as yf

    d = yf.Ticker(ticker).history(period="1d")
    return None if d.empty else round(float(d["Close"].iloc[-1]), 2)
