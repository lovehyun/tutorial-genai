# 10.mini_apps — 에이전트 실전 미니 앱

`1~9` 에서 배운 패턴(@tool · 빌트인 · 메모리 · HITL · 라우팅)을 **돌아가는 앱**으로 조립한 POC 모음.
모든 코드는 "최소한의 컨셉 시연" 을 목표로 하며, **키가 없어도** 안내 메시지/콘솔 폴백으로 흐름을 볼 수 있게 만들었습니다.

| 앱 | 한 줄 | 핵심 패턴 |
|---|---|---|
| `1.webscan_app/` | 시스템 점검 어시스턴트 (Flask) | `@tool` 6종 + create_agent + 메모리 |
| `2.finance_bot/` | 뉴스/기업정보/환율/주가 조회 봇 (CLI) | 멀티툴 라우팅 |
| `3.trading_bot/` | 조건 충족 시 **이메일 승인(HITL)** 후 가상 거래 | cron 잡 + out-of-band HITL |

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

## 키 설정
`.env.example` 참고 → `.env` 로 복사(또는 상위 `2.langchain/.env`).
- 필수: `OPENAI_API_KEY`
- 선택: `NAVER_CLIENT_ID/SECRET`(뉴스), `SERPER_API_KEY`(기업정보), `EMAIL_*`(이메일 HITL)
- 키 없으면 해당 기능만 콘솔 폴백/안내 메시지로 대체 — 앱은 계속 동작
