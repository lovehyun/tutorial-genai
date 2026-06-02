"""
4.trading_bot_web — 자연어 '챗봇' 으로 묻고 예약/매매하는 가상 트레이딩 비서.
⚠️ 실제 거래/환전 없음. 가상 머니 + 자체 랜덤 시세. 개념 시연용 샌드박스.

화면(단일 페이지):
  - 상단: 흐르는 시세 티커 + 내 잔고
  - 좌측: 내 상태 — 예약된 조건 / 알림 / 승인 요청 / 로그
  - 우측: 챗봇 — 자연어로 잔고·시세·환율을 묻고, 예약/알림/매매를 요청

핵심:
  - 우측 챗봇은 create_agent + 도구(get_balance/get_price/get_rate/schedule/trade_now).
  - 대화 중 도구가 동작하면 좌측 상태(예약/승인/알림)에 등록된다.
  - 조건부 예약은 APScheduler 가 5초마다 점검 → 충족 시:
      · alert        → 좌측 '알림' (거래 X, 확인만)
      · buy/sell/exchange → 좌측 '승인 요청' (예 누르면 실제 가상 체결, 잔액 부족이면 실패)

실행:  python app.py   → http://localhost:5003
  ※ pip install flask apscheduler langchain langchain-openai python-dotenv
"""

import uuid

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

import wallet
import market

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static")

rules: dict[str, dict] = {}     # id -> 조건부 예약 규칙
pending: dict[str, dict] = {}   # token -> 매매/환전 승인 대기 (예/아니오)
alerts: dict[str, dict] = {}    # id -> 발동된 알림 (확인만)
log: list[str] = []             # 최근 이벤트
auto = {"on": False}            # 자동 승인 모드 — True 면 매매/환전을 묻지 않고 바로 체결


# ─── 상태 헬퍼 ───────────────────────────────────────────────
def _say(msg: str):
    print(msg)
    log.append(msg)
    del log[:-10]


def _met(value, comparator, threshold) -> bool:
    return value <= threshold if comparator == "<=" else value >= threshold


def _is_rate(r: dict) -> bool:
    return r["action"] == "exchange" or str(r.get("ticker", "")).upper() in ("USD/KRW", "KRW/USD")


def _value(r: dict) -> float:
    return market.usd_krw() if _is_rate(r) else market.stock_price(r["ticker"])


def _watch(r: dict) -> str:
    return "환율" if _is_rate(r) else f"{r['ticker']} 주가"


def _desc(r: dict) -> str:
    when = "지금" if r.get("comparator") == "now" else f"{r['comparator']} {r['threshold']}"
    if r["action"] == "alert":
        return f"{_watch(r)} {when} 도달 알림"
    if r["action"] == "exchange":
        return f"환율 {when} → {int(r['amount']):,}원 환전"
    verb = "매수" if r["action"] == "buy" else "매도"
    return f"{r['ticker']} 주가 {when} → {int(r['amount'])}주 {verb}"


def _execute(o: dict):
    """승인된 주문을 실제(가상) 체결한다. (buy/sell/exchange)"""
    if o["action"] == "buy":
        return wallet.buy_stock(o["ticker"], int(o["amount"]), o["value"])
    if o["action"] == "sell":
        return wallet.sell_stock(o["ticker"], int(o["amount"]), o["value"])
    return wallet.exchange_krw_to_usd(o["amount"], o["value"])


# ─── 챗봇 에이전트 도구 (모두 가상) ─────────────────────────
@tool
def get_balance() -> dict:
    """내 지갑 잔고 조회: 현금 KRW, 달러 USD, 보유 주식 수량."""
    return wallet.load()


@tool
def get_price(ticker: str) -> str:
    """특정 종목의 현재 주가(USD)를 조회한다. 예: AAPL, NVDA, TSLA, MSFT."""
    return f"{ticker} = {market.stock_price(ticker)} USD"


@tool
def get_rate() -> str:
    """현재 환율(1 USD = ? KRW)을 조회한다."""
    return f"USD/KRW = {market.usd_krw()}"


@tool
def schedule(action: str, comparator: str, threshold: float, ticker: str = "AAPL", amount: float = 0) -> str:
    """조건이 충족되면 알림/매매하도록 '예약' 한다 (나중에 시세가 조건에 닿으면 발동).
    action: 'alert'(알림만)/'buy'(매수)/'sell'(매도)/'exchange'(환전)
    comparator: '<='(이하/떨어지면) 또는 '>='(이상/오르면)
    threshold: 기준값 — 주가는 USD, 환율은 KRW. 환율을 감시하면 ticker='USD/KRW'.
    ticker: 감시/거래 종목 (exchange 는 무시)
    amount: buy/sell=수량(주), exchange=환전할 금액(KRW), alert 은 0
    """
    if action not in ("alert", "buy", "sell", "exchange") or comparator not in ("<=", ">="):
        return "잘못된 action 또는 comparator 입니다."
    r = {"action": action, "ticker": ticker, "comparator": comparator,
         "threshold": float(threshold), "amount": float(amount), "text": "(챗봇 예약)"}
    rules[uuid.uuid4().hex[:8]] = r
    _say(f"📝 예약 추가: {_desc(r)}")
    return f"예약했습니다 — {_desc(r)}"


@tool
def trade_now(action: str, amount: float, ticker: str = "AAPL") -> str:
    """지금 즉시 매매/환전을 '승인 대기' 로 올린다. 실제(가상) 체결은 사용자가 화면에서 '예' 를 눌러야 한다.
    action: 'buy'(매수)/'sell'(매도)/'exchange'(환전).  amount: 수량(주) 또는 환전 금액(KRW).  ticker: 종목.
    """
    if action not in ("buy", "sell", "exchange"):
        return "trade_now 는 buy/sell/exchange 만 가능합니다."
    r = {"action": action, "ticker": ticker, "comparator": "now", "threshold": 0,
         "amount": float(amount), "text": "(챗봇 즉시 요청)"}
    value = market.usd_krw() if _is_rate(r) else market.stock_price(ticker)
    pending[uuid.uuid4().hex[:8]] = {**r, "value": value}
    _say(f"❓ 승인 대기: {_desc(r)} (현재값 {value})")
    return "승인 대기에 올렸습니다. 화면 왼쪽에서 '예' 를 누르면 체결됩니다."


@tool
def list_schedules() -> list:
    """현재 예약된 조건(알림/매매) 목록을 조회한다. 취소 전에 먼저 호출해 id 를 확인한다.
    각 항목: {"id": ..., "예약": 설명}."""
    return [{"id": k, "예약": _desc(v)} for k, v in rules.items()]


@tool
def cancel_schedule(rule_id: str) -> str:
    """예약된 조건을 취소(삭제)한다. rule_id 는 반드시 list_schedules 로 먼저 확인한 값이어야 한다.
    (사용자가 '환율 알림 취소' 처럼 말하면 → list_schedules 로 목록을 보고 알맞은 id 를 골라 호출)"""
    r = rules.pop(rule_id, None)
    if not r:
        return f"해당 예약(id={rule_id})을 찾을 수 없습니다. list_schedules 로 다시 확인하세요."
    _say(f"🗑️ 예약 취소: {_desc(r)}")
    return f"예약을 취소했습니다 — {_desc(r)}"


SYSTEM = (
    "당신은 '가상' 트레이딩 비서입니다. 실제 거래는 일어나지 않습니다.\n"
    "- 잔고/주가/환율 질문은 도구(get_balance/get_price/get_rate)로 확인해 한국어로 간단히 답하세요.\n"
    "- '~하면 알려줘/사줘/팔아줘/환전해줘' 같은 조건부 요청은 schedule 로 예약하세요 "
    "(alert=알림만, buy/sell/exchange=매매·환전).\n"
    "- '지금 사줘/팔아줘/환전해줘' 는 trade_now 로 승인 대기에 올리세요. "
    "매매·환전은 사용자가 화면에서 '예' 를 눌러야 체결됩니다.\n"
    "- '~예약/알림 취소(삭제)해줘' 는 먼저 list_schedules 로 목록·id 를 확인한 뒤 "
    "알맞은 id 로 cancel_schedule 을 호출하세요.\n"
    "- 모르는 값은 추측하지 말고 반드시 도구로 확인하세요."
)
chat_agent = create_agent(
    ChatOpenAI(model="gpt-4o-mini", temperature=0),
    [get_balance, get_price, get_rate, schedule, trade_now, list_schedules, cancel_schedule],
    system_prompt=SYSTEM,
    checkpointer=MemorySaver(),
)


# ─── 주기 모니터링: 예약 조건 충족 시 알림 / 승인 대기로 ─────
def monitor():
    market.tick()
    for rid, r in list(rules.items()):
        value = _value(r)
        if not _met(value, r["comparator"], r["threshold"]):
            continue
        del rules[rid]                       # one-shot
        o = {**r, "value": value}
        if r["action"] == "alert":
            alerts[uuid.uuid4().hex[:8]] = o
            _say(f"🔔 알림: {_desc(r)} (현재값 {value})")
        elif auto["on"]:                     # 자동 승인 — 묻지 않고 바로 체결
            ok, msg = _execute(o)
            _say(("✅ [자동] " if ok else "❌ [자동] ") + msg)
        else:                                # 수동 — 승인 대기로
            pending[uuid.uuid4().hex[:8]] = o
            _say(f"❓ 승인 대기: {_desc(r)} (현재값 {value})")


# ─── 라우트 ─────────────────────────────────────────────────
@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/chat")
def chat():
    data = request.json or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify(reply="")
    cfg = {"configurable": {"thread_id": data.get("thread_id") or "web"}}
    try:
        result = chat_agent.invoke({"messages": [("user", msg)]}, config=cfg)
        return jsonify(reply=result["messages"][-1].content)
    except Exception as e:
        return jsonify(reply=f"(오류) {e}")


@app.post("/approve/<token>")
def approve(token):
    o = pending.pop(token, None)
    if not o:
        return jsonify(ok=False, msg="만료되었거나 없는 주문입니다.")
    ok, msg = _execute(o)
    _say(("✅ " if ok else "❌ ") + msg)
    return jsonify(ok=ok, msg=msg)


@app.post("/auto/<token>")
def auto_approve(token):
    """이 주문을 체결하고 '자동 승인' 을 켠다 → 이후 조건 충족 매매는 묻지 않고 바로 체결.
    이미 대기 중인 다른 주문도 함께 체결한다."""
    auto["on"] = True
    _say("🔁 자동 승인 ON")
    msgs = []
    clicked = pending.pop(token, None)
    for o in ([clicked] if clicked else []) + [pending.pop(t) for t in list(pending)]:
        ok, msg = _execute(o)
        _say(("✅ [자동] " if ok else "❌ [자동] ") + msg)
        msgs.append(msg)
    return jsonify(ok=True, msg=" / ".join(msgs) or "자동 승인을 켰습니다.")


@app.post("/auto_off")
def auto_off():
    auto["on"] = False
    _say("⏸️ 자동 승인 OFF")
    return jsonify(ok=True)


@app.post("/reject/<token>")
def reject(token):
    o = pending.pop(token, None)
    if o:
        _say(f"🚫 거부: {_desc(o)}")
    return jsonify(ok=bool(o))


@app.post("/dismiss/<aid>")
def dismiss(aid):
    """알림 확인(닫기) — 거래가 아니라 단순 확인."""
    return jsonify(ok=bool(alerts.pop(aid, None)))


@app.post("/delete/<rid>")
def delete(rid):
    r = rules.pop(rid, None)
    if r:
        _say(f"🗑️ 예약 삭제: {_desc(r)}")
    return jsonify(ok=bool(r))


@app.get("/state")
def state():
    return jsonify(
        wallet=wallet.load(),
        rules=[{"id": k, "desc": _desc(v), **v} for k, v in rules.items()],
        pending=[{"token": k, "desc": _desc(v), **v} for k, v in pending.items()],
        alerts=[{"id": k, "desc": _desc(v), **v} for k, v in alerts.items()],
        prices={"USD/KRW": market.usd_krw(), **market.stocks()},
        auto=auto["on"],
        log=log[-10:],
    )


if __name__ == "__main__":
    print("4.trading_bot_web — http://localhost:5003  (Ctrl+C 종료)")
    print(f"  지갑: {wallet.load()}")
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(monitor, "interval", seconds=5)
    sched.start()
    app.run(port=5003, use_reloader=False)
