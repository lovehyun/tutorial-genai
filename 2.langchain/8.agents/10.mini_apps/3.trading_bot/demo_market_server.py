"""
데모용 가짜 시세 서버 (Flask) — 실제 API 대신 '랜덤 워크' 로 매초 변하는 환율/주가 제공.
⚠️ 실제 시장 데이터 아님. 트레이딩 봇 데모를 빠르게(매초 변동) 돌려보기 위한 가짜 시세.

페이지:
  GET /                                  → 환율/주가가 매초 갱신되는 대시보드 (브라우저로 확인)
API (트레이딩 봇이 호출):
  GET /api/exchange?base=USD&target=KRW  → {"base","target","rate"}
  GET /api/stock/<ticker>                → {"ticker","price"}

실행:  python demo_market_server.py        → http://localhost:5002
연동:  3.trading_bot 의 .env 에  DEMO_MARKET_URL=http://localhost:5002  설정하면
       market.py 가 실제 API 대신 이 서버를 조회한다 (실제 API 경로는 그대로 유지).

  ※ pip install flask
"""

import random
import threading
import time

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="/static")

# 초기 시세 (가짜). 트레이딩 봇 기본 임계값(환율 1500, AAPL 150) 근처라 조건이 자주 걸린다.
state = {
    "USD_KRW": 1480.0,
    "stocks": {"AAPL": 152.0, "MSFT": 420.0, "NVDA": 120.0, "005930.KS": 75000.0},
}


def _walk(value: float, pct: float = 0.004) -> float:
    """value 를 ±pct 범위로 랜덤 워크."""
    return round(value * (1 + random.uniform(-pct, pct)), 2)


def _ticker():
    """매초 모든 시세를 조금씩 변동시키는 백그라운드 루프."""
    while True:
        state["USD_KRW"] = _walk(state["USD_KRW"])
        for t in state["stocks"]:
            state["stocks"][t] = _walk(state["stocks"][t])
        time.sleep(1)


@app.route("/api/exchange")
def api_exchange():
    base = request.args.get("base", "USD").upper()
    target = request.args.get("target", "KRW").upper()
    # 데모는 USD→KRW 만 변동, 나머지 쌍은 1.0 으로 단순화 (POC)
    rate = state["USD_KRW"] if (base, target) == ("USD", "KRW") else 1.0
    return jsonify({"base": base, "target": target, "rate": rate})


@app.route("/api/stock/<ticker>")
def api_stock(ticker):
    price = state["stocks"].get(ticker)
    if price is None:                      # 모르는 종목은 즉석 생성 (데모)
        price = state["stocks"][ticker] = round(random.uniform(50, 300), 2)
    return jsonify({"ticker": ticker, "price": price})


@app.route("/")
def home():
    # 대시보드 HTML 은 static/index.html 로 분리 (Chart.js 시계열 차트 포함)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    threading.Thread(target=_ticker, daemon=True).start()
    print("데모 시세 서버 — http://localhost:5002  (Ctrl+C 종료)")
    app.run(port=5002, use_reloader=False)
