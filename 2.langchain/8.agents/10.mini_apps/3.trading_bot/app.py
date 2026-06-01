"""
가상 트레이딩 봇 (POC) — 주기 모니터링 + '이메일 승인(HITL)' 후 가상 거래.

⚠️ 실제 거래/환전 없음. 가상 머니 + 가짜 체결. 개념 시연 전용 샌드박스.

핵심 개념 — out-of-band HITL (비동기 사람 승인):
  6.hitl_streaming/6.1 의 interrupt_before 는 '같은 프로세스 안에서 즉시' 멈춰 물어봤다.
  여기선 에이전트가 '혼자 주기적으로 돌다가' 위험 액션(환전/매수) 직전에 멈추고,
  사람에게 '이메일' 로 승인을 요청한 뒤 → 사람이 'URL 클릭' 으로 나중에 승인/거부한다.
  (실무의 비동기 승인 워크플로우: 이메일/슬랙 승인 버튼과 같은 패턴)

흐름:
  1) APScheduler 가 주기적으로(cron) 환율/주가 조회
  2) 조건 충족 → 대기 주문(pending) 생성 + 승인 요청 이메일 발송
       (SMTP 키 없으면 콘솔에 메일 내용 + 승인/거부 URL 출력)
  3) 사람이 메일의 URL 클릭 → /approve/<token> | /reject/<token>
  4) 승인 시에만 wallet 갱신(가상 거래 실행), 거부 시 취소

실행:  python app.py   → http://localhost:5001  (Ctrl+C 종료)
  ※ pip install flask apscheduler requests yfinance python-dotenv
"""

import os
import uuid

from dotenv import load_dotenv
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import wallet
import market
from notifier import send_email

load_dotenv()

BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5001")
USD_RATE_THRESHOLD = float(os.getenv("USD_RATE_THRESHOLD", "1500"))   # 환율 이 값 이하 → 환전 신호
STOCK_TICKER = os.getenv("WATCH_TICKER", "AAPL")                       # 감시할 주식
STOCK_BUY_BELOW = float(os.getenv("STOCK_BUY_BELOW", "150"))           # 이 값 이하 → 매수 신호
EXCHANGE_KRW = 1_000_000                                               # 1회 환전액(가상)

app = Flask(__name__)
pending: dict[str, dict] = {}   # token -> 대기 중인 HITL 주문


def monitor():
    """주기 실행(cron 잡): 조건 확인 → 충족 시 승인 요청 이메일."""
    rate = market.usd_krw()
    print(f"[모니터] USD/KRW={rate} (임계 {USD_RATE_THRESHOLD})")

    # 조건 1) 환율이 임계값 이하 → KRW→USD 환전 승인 요청
    if rate <= USD_RATE_THRESHOLD and not _has_pending("exchange"):
        _request_approval(
            {"type": "exchange", "amount_krw": EXCHANGE_KRW, "rate": rate},
            "[트레이딩봇] 환전 승인 요청",
            f"환율 {rate} KRW/USD ≤ 임계 {USD_RATE_THRESHOLD}.\n"
            f"{EXCHANGE_KRW:,} KRW 를 USD 로 환전할까요?",
        )

    # 조건 2) 감시 주식이 매수가 이하 → 매수 승인 요청 (USD 보유 시)
    price = market.stock_price(STOCK_TICKER)
    print(f"[모니터] {STOCK_TICKER}={price} (매수 임계 ≤ {STOCK_BUY_BELOW})")
    if price and price <= STOCK_BUY_BELOW and wallet.load()["USD"] >= price and not _has_pending("buy"):
        _request_approval(
            {"type": "buy", "ticker": STOCK_TICKER, "qty": 1, "price": price},
            "[트레이딩봇] 매수 승인 요청",
            f"{STOCK_TICKER} {price} USD ≤ 임계 {STOCK_BUY_BELOW}.\n1주 매수할까요?",
        )


def _has_pending(kind: str) -> bool:
    return any(p["type"] == kind for p in pending.values())


def _request_approval(order: dict, subject: str, summary: str):
    token = uuid.uuid4().hex[:8]
    pending[token] = order
    body = (
        f"{summary}\n\n"
        f"✅ 승인: {BASE_URL}/approve/{token}\n"
        f"❌ 거부: {BASE_URL}/reject/{token}\n"
    )
    send_email(subject, body)


@app.route("/")
def home():
    return {"wallet": wallet.load(), "pending": pending,
            "rate_threshold": USD_RATE_THRESHOLD, "watch": STOCK_TICKER}


@app.route("/approve/<token>")
def approve(token):
    order = pending.pop(token, None)
    if not order:
        return "만료되었거나 존재하지 않는 주문입니다."
    if order["type"] == "exchange":
        ok, msg = wallet.exchange_krw_to_usd(order["amount_krw"], order["rate"])
    else:  # buy
        ok, msg = wallet.buy_stock(order["ticker"], order["qty"], order["price"])
    return f"[{'승인 처리' if ok else '실패'}] {msg}<br>지갑: {wallet.load()}"


@app.route("/reject/<token>")
def reject(token):
    order = pending.pop(token, None)
    return "[거부] 주문이 취소되었습니다." if order else "존재하지 않는 주문"


if __name__ == "__main__":
    print(f"가상 트레이딩 봇 시작 — {BASE_URL}  (Ctrl+C 종료)")
    print(f"  지갑: {wallet.load()}")
    monitor()  # 시작 즉시 1회 점검

    sched = BackgroundScheduler(daemon=True)
    # cron 잡 등록: 30초마다 (실무 예: CronTrigger(hour=9, minute=0) = 매일 09:00)
    sched.add_job(monitor, CronTrigger(second="*/30"))
    sched.start()

    app.run(port=5001, use_reloader=False)
