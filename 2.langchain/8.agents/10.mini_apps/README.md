# 10.mini_apps — 에이전트 실전 미니 앱

`1~9` 에서 배운 패턴(@tool · 빌트인 · 메모리 · HITL · 라우팅)을 **돌아가는 앱**으로 조립한 POC 모음.
모든 코드는 "최소한의 컨셉 시연" 을 목표로 하며, **키가 없어도** 안내 메시지/콘솔 폴백으로 흐름을 볼 수 있게 만들었습니다.

| 앱 | 한 줄 | 핵심 패턴 |
|---|---|---|
| `1.webscan_app/` | 시스템 점검 어시스턴트 (Flask) | `@tool` 6종 + create_agent + 메모리 |
| `2.finance_bot/` | 뉴스/기업정보/환율/주가 조회 봇 (CLI) | 멀티툴 라우팅 |
| `3.trading_bot/` | 조건 충족 시 **이메일 승인(HITL)** 후 가상 거래 | cron 잡 + out-of-band HITL |
| `4.trading_bot_web/` | **챗봇**으로 잔고·시세 묻고 예약/매매 → 충족 시 **알림/승인(예·아니오)** 후 가상 거래 | 대화형 에이전트(도구 5종) + 웹 HITL |

---

## 1.webscan_app — 시스템 점검 (기존)
Flask + create_agent + `@tool` 6종(포트/SSL/웹/리소스/프로세스/네트워크) + MemorySaver.
```bash
cd 1.webscan_app && python app.py   # → http://localhost:5000
```

## 2.finance_bot — 금융 조회 봇 (CLI)
자연어로 물으면 LLM 이 알맞은 도구를 골라 답한다.
- `get_news`(네이버) · `get_company_info`(구글/Serper) · `get_exchange_rate`(open.er-api, 키X) · `get_stock_price`(yfinance, 키X)
```bash
pip install langchain langchain-openai requests yfinance python-dotenv
cd 2.finance_bot && python app.py
# 데모 질문 자동 실행 후 대화형. 키 없는 환율/주가는 바로 동작.
```

## 3.trading_bot — 가상 트레이딩 + 이메일 HITL  ⚠️ 가상머니 샌드박스
**실제 거래/환전 없음.** 가상 머니 1천만원으로 시작하는 개념 시연용.

```bash
pip install flask apscheduler requests yfinance python-dotenv
cd 3.trading_bot && python app.py   # → http://localhost:5001
```

**데모 시세 서버** (`demo_market_server.py`) — 실제 API 대신 **매초 랜덤 변동**하는 가짜 환율/주가:
```bash
python demo_market_server.py        # → http://localhost:5002 (브라우저로 시세 변동 확인)
# 다른 터미널: .env 에 DEMO_MARKET_URL=http://localhost:5002 설정 후 봇 실행
#   → market.py 가 실제 API 대신 데모 서버 조회 (조건이 매초 바뀌어 HITL 플로우 빠르게 시연)
```
> 실제 API 경로(open.er-api / yfinance)는 그대로 유지 — `DEMO_MARKET_URL` 유무로 분기.

동작:
1. **APScheduler(cron 잡)** 가 30초마다 환율/주가 조회
2. 조건 충족(환율 ≤ 임계 / 주가 ≤ 매수가) → **대기 주문 생성 + 승인 요청 이메일**
   - SMTP 키 없으면 **콘솔에 메일 내용 + 승인/거부 URL** 출력
3. 사람이 메일의 **URL 클릭** → `/approve/<token>` 또는 `/reject/<token>`
4. **승인 시에만** 가상 거래 실행(지갑 갱신), 거부 시 취소

> ### 왜 이게 중요한가 — 두 가지 HITL
> - `6.hitl_streaming/6.1` = **인프로세스** HITL: 같은 실행 안에서 즉시 멈춰 승인받음
> - 여기 `3.trading_bot` = **out-of-band(비동기)** HITL: 에이전트가 혼자 주기적으로 돌다가,
>   위험 액션 직전 멈추고 **이메일로 승인 요청** → 사람이 나중에 URL 로 승인/거부
>
> 실무의 "이메일/슬랙 승인 버튼" 워크플로우가 바로 이 패턴입니다.

상태 확인: 브라우저로 `http://localhost:5001/` → 지갑/대기주문 JSON.

---

## 4.trading_bot_web — 챗봇 가상 트레이딩 (대화형 에이전트)  ⚠️ 가상머니 샌드박스
**실제 거래/환전 없음.** 3.trading_bot 의 웹 버전 — **챗봇과 대화**하며 잔고·시세·환율을 묻고,
예약/알림/매매를 요청한다. 외부 시세 서버 없이 **단독 실행**.

```bash
pip install flask apscheduler langchain langchain-openai python-dotenv
cd 4.trading_bot_web && python app.py   # → http://localhost:5003
```

**화면 구성**
- 상단: **흐르는 시세 티커** + 내 **잔고**(KRW/USD/보유주식)
- 좌측: 내 상태 — **예약된 조건 / 알림 / 승인 요청 / 로그**
- 우측: **챗봇** — 자연어로 묻고 답 (잔고·환율·주가), 예약·매매 요청

**핵심 — 대화형 에이전트 + 도구**
- 우측 챗봇 = `create_agent` + 도구 5종 (`MemorySaver` 로 대화 기억):
  - `get_balance` / `get_price` / `get_rate` — 잔고·주가·환율 질의응답
  - `schedule(action, comparator, threshold, ticker, amount)` — 조건부 **예약** (alert/buy/sell/exchange)
  - `trade_now(action, amount, ticker)` — **즉시** 매매/환전을 승인 대기로
- 대화 중 도구가 동작하면 → **좌측 상태에 등록**된다.

**알림 vs 매매 (구분)**
- 🔔 **알림(alert)** — 목표가 '도달 알림만'. 거래 없음, **확인** 으로 닫기.
- ❓ **매매/환전(buy·sell·exchange)** — **예** 누르면 실제(가상) 체결. **잔액·보유수량 부족 시 실패.**
  - 승인 카드의 **[자동(예)]** 을 누르면 이 건을 체결하고 **자동 승인 ON** — 이후 조건 충족 매매는
    묻지 않고 바로 체결됩니다(상단 배너의 **[끄기]** 로 해제). HITL: 수동 승인 ↔ 자동의 스펙트럼.

동작:
1. 챗봇에 자연어 입력 → 에이전트가 도구를 호출 (질의응답 / 예약 / 즉시요청)
2. **APScheduler** 가 5초마다 자체 랜덤 시세 갱신·점검 → 예약 조건 충족 시
   `alert` 는 좌측 '알림', `buy/sell/exchange` 는 '승인 요청' 으로 (각 규칙 1회성)
3. 좌측에서 알림은 **확인**, 승인 요청은 **예/아니오** — **예** → `wallet` 갱신(가상 체결)

> 예시 대화: "내 잔고 알려줘" · "지금 환율 얼마야?" · "AAPL 150달러 이하로 떨어지면 1주 사줘"
> · "환율 1500원 넘으면 알려줘" · "지금 100만원 환전해줘" · "환율 알림 취소해줘" · "내 예약 뭐 있어?"
> 매수는 USD 가 있어야 하므로, 먼저 환전으로 USD 를 만든 뒤 매수하는 흐름을 시연할 수 있습니다.

---

## 키 설정
`.env.example` 참고 → `.env` 로 복사(또는 상위 `2.langchain/.env`).
- 필수: `OPENAI_API_KEY`
- 선택: `NAVER_CLIENT_ID/SECRET`(뉴스), `SERPER_API_KEY`(기업정보), `EMAIL_*`(이메일 HITL)
- 키 없으면 해당 기능만 콘솔 폴백/안내 메시지로 대체 — 앱은 계속 동작
