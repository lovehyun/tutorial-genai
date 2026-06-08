"""
가상 지갑 — ⚠️ 실제 거래 없음. JSON 파일에 현금(KRW)/달러(USD)/보유주식 저장.
가상 머니 1천만원으로 출발. (개념 시연용 샌드박스)
"""

import json
import os

WALLET_FILE = os.path.join(os.path.dirname(__file__), "wallet.json")
DEFAULT = {"KRW": 10_000_000, "USD": 0.0, "stocks": {}}


def load() -> dict:
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, encoding="utf-8") as f:
            return json.load(f)

    return dict(DEFAULT)


def save(w: dict):
    with open(WALLET_FILE, "w", encoding="utf-8") as f:
        json.dump(w, f, ensure_ascii=False, indent=2)


def exchange_krw_to_usd(amount_krw: float, rate: float):
    """KRW → USD 가상 환전 (rate = 1 USD 당 KRW)."""
    w = load()
    if w["KRW"] < amount_krw:
        return False, "KRW 잔액 부족"
    
    w["KRW"] -= amount_krw
    w["USD"] = round(w["USD"] + amount_krw / rate, 2)
    save(w)
    
    return True, f"환전 완료: {amount_krw:,.0f} KRW → {round(amount_krw / rate, 2)} USD"


def buy_stock(ticker: str, qty: int, price: float):
    """가상 주식 매수 (price = 1주당 USD)."""
    w = load()
    cost = qty * price
    if w["USD"] < cost:
        return False, f"USD 잔액 부족 (필요 {cost}, 보유 {w['USD']})"

    w["USD"] = round(w["USD"] - cost, 2)
    w["stocks"][ticker] = w["stocks"].get(ticker, 0) + qty
    save(w)
    return True, f"매수 완료: {ticker} {qty}주 @ {price} USD (총 {round(cost, 2)} USD)"
