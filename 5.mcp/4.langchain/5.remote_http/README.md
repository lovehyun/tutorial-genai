# 4.langchain/5.remote_http — 원격(HTTP) MCP 서버 + LangChain 에이전트

지금까지의 `2~4.langchain` 예제는 전부 **stdio** — 클라이언트가 서버를 자식 프로세스로 띄웠다.
여기서는 서버를 **먼저 띄워두고 URL 로 접속**한다. 실무에서 더 흔한 형태다
(사내 공용 MCP 서버 몇 대 + 각자 노트북의 에이전트).

## 이 폴더의 두 가지 질문에 대한 답

**Q. 서버에도 LangChain 이 필요한가? → 아니오.**
이 폴더의 서버 두 개 모두 `langchain` import 가 한 줄도 없다. MCP 서버의 책임은
"도구 목록/스키마를 노출하고, 호출되면 실행해 결과를 돌려주는 것" 뿐이고,
*어떤 도구를 쓸지 LLM 이 고르게 하는* 일은 전적으로 클라이언트(에이전트) 몫이다.
덕분에 같은 서버를 Claude Desktop · Codex · 순수 `ClientSession` 어디에 붙여도 그대로 동작한다.
(서버에 LangChain 이 정당해지는 경우는 **도구 자체가 LLM 파이프라인**일 때 — RAG 검색/요약 체인 — 뿐이다.)

**Q. 그럼 전송 방식을 바꾸면 에이전트 코드가 달라지나? → 아니오.**
바뀌는 건 설정 딕셔너리 한 덩어리뿐이다.

```python
# stdio (1.quickstart)                        # http (여기)
{"command": "python", "args": [SERVER],       {"url": "http://127.0.0.1:8000/mcp",
 "transport": "stdio"}                         "transport": "streamable_http"}
```
`get_tools()` 이후 코드(도구 변환 → `create_agent` → `ainvoke`)는 완전히 동일하다.

## 파일

| 파일 | 역할 | 포트 |
|---|---|---|
| `1.server_simple.py` | 계산/인사 도구 서버 (LangChain 없음) | 8000 |
| `2.client_agent.py` | 원격 서버에 붙는 LangChain 에이전트 | — |
| `3.server_stock.py` | **yfinance 로 실제 주가를 조회**하는 서버 (LangChain 없음) | 8001 |
| `4.client_stock_agent.py` | 주식 정보 에이전트 (도구 여러 번 호출) | — |
| `5.client_multi.py` | 두 원격 서버를 한 에이전트에 동시 연결 | — |
| `6.client_interactive.py` | **대화형** — 직접 질문하며 멀티턴 대화 (`그럼 MS는?` 이 통한다) | — |

## 실행

```bash
cd 8.mcp/4.langchain/5.remote_http
pip install mcp yfinance langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
# .env 에 OPENAI_API_KEY

# 터미널 1
python 1.server_simple.py      # http://127.0.0.1:8000/mcp
# 터미널 2
python 2.client_agent.py
```

```bash
# 주가 서버 (터미널 1 → 2 순서)
python 3.server_stock.py       # http://127.0.0.1:8001/mcp
python 4.client_stock_agent.py

# 두 서버를 동시에 (8000, 8001 을 각각 띄워둔 뒤)
python 5.client_multi.py

# 대화형 — 직접 질문을 입력한다 (3.server_stock.py 가 떠 있어야 함)
python 6.client_interactive.py
```
`6.client_interactive.py` 는 `checkpointer` + 고정 `thread_id` 로 대화를 기억한다.
이어지는 질문이 통하는지 확인해 보기:
```
애플 주가 알려줘  →  그럼 마이크로소프트는?  →  둘 중 최근 1개월 더 오른 쪽은?
```
> stdio 예제와 달리 **서버가 자동으로 뜨지 않는다.** 먼저 띄워두는 것이 이 단계의 핵심이다.

## 관전 포인트

- **`1.server_simple` vs `3.server_stock`** — 전자의 `add` 는 LLM 혼자서도 푼다.
  후자의 주가는 LLM 이 **절대 모르는 정보**라 도구를 부를 수밖에 없다.
  MCP 를 쓰는 진짜 이유가 드러나는 지점.
- **역할 분담** — '애플' → `AAPL` 변환은 LLM 의 상식이, 시세 조회는 도구가 담당한다.
- **다중 호출** — "애플 vs 마이크로소프트 1개월 비교" 한 문장에 도구가 여러 번 불린다.
  몇 번을 어떤 순서로 부를지는 LLM 이 스스로 계획한다.
- **에러를 raise 하지 않고 문자열로 반환** — 에이전트가 그 문장을 읽고 티커를 고쳐 재시도할 수 있다.

## 자주 틀리는 곳

- **하이픈 vs 언더스코어**
  - 서버: `mcp.run(transport="streamable-http")` ← 하이픈. `"http"` 는 `ValueError`.
  - 클라: `{"transport": "streamable_http"}` ← 언더스코어. adapters 는 이것만 인식한다.
- **`streamable_http_client` 를 import 하지 않아도 되나?** — 된다.
  [1.basic/3.transports_http](../../1.basic/3.transports_http/) 의 손수 만든 클라이언트는 그 함수를 직접 불렀지만,
  여기서는 `MultiServerMCPClient` 가 대신 호출해 준다.
  설정의 `"streamable_http"` 문자열은 *"그 함수를 써라"* 는 선택 스위치일 뿐이다
  (`"stdio"` → `stdio_client(...)`, `"streamable_http"` → `streamable_http_client(url)`).
- **호스트/포트는 `run()` 이 아니라 `FastMCP()` 생성자에서** 지정한다. `run()` 은 `transport` 만 받는다.
- **엔드포인트 경로는 `/mcp`** 다. `http://127.0.0.1:8000` 만 주면 붙지 않는다.
- yfinance 는 야후 파이낸스 비공식 스크래핑이라 **지연 시세**이고 호출이 잦으면 일시적으로 막힐 수 있다. 학습·데모용.

## 추천 순서

`1.server_simple` + `2.client_agent` → `3.server_stock` + `4.client_stock_agent` → `5.client_multi` → `6.client_interactive`

다음: 되돌릴 수 없는 도구(삭제·발송)가 섞이면 실행 전 사람 승인이 필요하다 → [6.human_in_loop](../6.human_in_loop/)
