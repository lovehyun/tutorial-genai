# 5.multi_mcp_concierge — 한 챗봇, 두 외부 MCP 서버 (쇼핑몰 + 여행사)

내 사이트의 챗봇 하나가 **서로 다른 두 회사의 MCP 서버**(쇼핑몰·여행사)에 동시에 붙어
사용자를 대신해 쇼핑하고 여행을 예약한다. [`4.chatbot_web`](../4.chatbot_web/)(서버 1개)의 **멀티서버 확장판**.

## 구조
```
                           ┌───────────────┐
사용자 ──웹 채팅──▶  app.py │  create_agent  │── MultiServerMCPClient ──┐
                           └───────────────┘                          │
                                  ┌───────────────────────────────────┴───┐
                                  ▼                                       ▼
                        shopping_server.py                       travel_server.py
                  (search_products·get_deal·                (search_trips·book_trip·
                   place_order·list_orders)                  list_bookings)
```

| 파일 | 역할 |
|---|---|
| `shopping_server.py` | **쇼핑몰 MCP** — 상품 검색 / 할인 / 주문 / 주문목록 |
| `travel_server.py` | **여행사 MCP** — 여행 검색 / 예약 / 예약목록 |
| `app.py` | **Flask 챗봇** — 두 서버를 `MultiServerMCPClient`로 묶어 `create_agent` |
| `templates/index.html` | 채팅 UI (호출한 MCP 도구 표시) |

## 실행
```bash
pip install flask langchain-openai langchain-mcp-adapters langgraph python-dotenv
# OPENAI_API_KEY 설정 (.env 또는 8.mcp/.env)
python app.py        # → http://localhost:5060
```
- 단순: *"노트북 할인가?"* · *"캐리어 2개 주문"* · *"제주도 여행 예약"*
- **복합**: *"도쿄 여행 예약하고 캐리어도 사줘"* → `book_trip`(여행사) + `place_order`(쇼핑몰) 순서 호출

## 관전 포인트
- **딕셔너리에 항목만 늘리면 멀티 서버** — `get_tools()`가 두 서버 도구를 한 묶음으로 합치고, 에이전트가 알아서 라우팅.
- 쇼핑몰·여행사는 **완전히 독립된 프로세스**(다른 회사인 척) — 내 챗봇은 MCP 표준으로만 연결한다.
- 실전 확장: 두 서버를 **HTTP(streamable-http) 원격**에 두면 진짜 "다른 사이트와 통신"이 된다
  (`{"url": "http://travel.com/mcp", "transport": "streamable_http"}` 형태).
