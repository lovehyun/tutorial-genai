"""
자체 랜덤-워크 시세 (4.trading_bot_web 전용) — 외부 API/서버 없이 매 tick 마다 조금씩 변동.
⚠️ 실제 시세 아님. 조건이 잘 걸리도록 흔한 임계값 근처에서 출발하는 가짜 시세.
"""

import random

_rate = 1480.0
_stocks = {"AAPL": 152.0, "NVDA": 120.0, "MSFT": 420.0, "TSLA": 240.0}


def _walk(v: float, pct: float = 0.01) -> float:
    """value 를 ±pct 범위로 랜덤 변동."""
    return round(v * (1 + random.uniform(-pct, pct)), 2)


def tick():
    """매 호출마다 환율/주가를 조금씩(±1%) 변동시킨다 (모니터가 주기적으로 호출)."""
    global _rate
    _rate = _walk(_rate)
    for t in _stocks:
        _stocks[t] = _walk(_stocks[t])


def usd_krw() -> float:
    return _rate


def stock_price(ticker: str) -> float:
    if ticker not in _stocks:               # 모르는 종목은 즉석 생성 (데모)
        _stocks[ticker] = round(random.uniform(50, 300), 2)
    return _stocks[ticker]


def stocks() -> dict:
    return dict(_stocks)
