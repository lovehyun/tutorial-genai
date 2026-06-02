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
        return False, f"환전 실패: KRW 잔액 부족 (필요 {amount_krw:,.0f}, 보유 {w['KRW']:,.0f})"

    w["KRW"] -= amount_krw
    w["USD"] = round(w["USD"] + amount_krw / rate, 2)
    save(w)
    return True, f"환전 완료: {amount_krw:,.0f} KRW → {round(amount_krw / rate, 2)} USD (환율 {rate})"


def buy_stock(ticker: str, qty: int, price: float):
    """가상 주식 매수 (price = 1주당 USD)."""
    w = load()
    cost = round(qty * price, 2)
    if w["USD"] < cost:
        return False, f"매수 실패: USD 잔액 부족 (필요 {cost}, 보유 {w['USD']}) — 먼저 환전하세요"

    w["USD"] = round(w["USD"] - cost, 2)
    w["stocks"][ticker] = w["stocks"].get(ticker, 0) + qty
    save(w)
    return True, f"매수 완료: {ticker} {qty}주 @ {price} USD (총 {cost} USD)"


def sell_stock(ticker: str, qty: int, price: float):
    """가상 주식 매도 (price = 1주당 USD)."""
    w = load()
    have = w["stocks"].get(ticker, 0)
    if have < qty:
        return False, f"매도 실패: {ticker} 보유 수량 부족 (필요 {qty}, 보유 {have})"

    proceeds = round(qty * price, 2)
    w["stocks"][ticker] = have - qty
    if w["stocks"][ticker] == 0:
        del w["stocks"][ticker]
    w["USD"] = round(w["USD"] + proceeds, 2)
    save(w)
    return True, f"매도 완료: {ticker} {qty}주 @ {price} USD (+{proceeds} USD)"
