# 1.basic/1.intro — MCP 첫 접촉 (LLM 없이)

MCP 를 **가장 처음** 만나는 곳. SDK 를 확인하고, `@mcp.tool()` 하나짜리 서버를 만들어
클라이언트로 **첫 왕복**(initialize → call_tool)을 해본다. 아직 LLM 은 없다.

> 서버는 단독 실행하면 stdin 대기로 멈춘다(고장 아님). **클라이언트가 서버를 자식 프로세스로 띄운다.**

## 학습 순서

| 단계 | 파일 | 무엇을 보나 |
|---|---|---|
| 0 | `0.asyncio_eventloop/` | (선행) MCP 가 왜 async 인지 — 이벤트 루프 기초 |
| 1 | `1.mcp_version.py` | 설치된 `mcp` SDK 버전 확인 |
| 2 | `2.mcp_docs.py` | SDK 구조 둘러보기 (FastMCP / ClientSession 등) |
| 3 | `3.hello_server.py` | `@mcp.tool()` 하나로 첫 MCP 서버 (`hello`) |
| 4 | `4.hello_client.py` | 그 서버에 붙어 `call_tool("hello")` — **첫 왕복** (LLM 없이 수동 호출) |

### 5~6. (미리보기) LLM이 여러 도구 중 고르게 하기

1~4는 도구가 하나뿐이라 "부를지 말지"조차 고민이 없었다. 도구가 여러 개면 어떨까 — 그 첫 맛보기.
본격적인 LLM 자동호출은 [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)에서 이어서 다루지만,
같은 패턴을 이 폴더 서버로 먼저 확인해본다.

| 단계 | 파일 | 무엇을 보나 |
|---|---|---|
| 5 | `5.hello_server.py` | 도구 3개(`hello`/`get_date`/`get_time`)짜리 서버 — `3.hello_server.py`에 도구만 늘렸다 |
| 6 | `6.hello_client_langchain_llm.py` | `langchain-mcp-adapters`로 MCP 도구 → LangChain Tool 자동 변환, LLM이 질문 보고 도구·인자를 스스로 결정 |

```bash
pip install mcp langchain-mcp-adapters langchain-openai python-dotenv
python 6.hello_client_langchain_llm.py    # .env 에 OPENAI_API_KEY 필요
```
```
[질문] John 에게 인사해줘           → hello({'name': 'John'})       → "Hello, John!"
[질문] 지금 날씨는?                 → (도구 호출 없음)               → "날씨 정보를 제공할 수 있는 기능은 없습니다..."
[질문] 지금 날짜는?                 → get_date({})                  → "오늘 날짜는 2026년 8월 29일입니다."
[질문] 지금 시간은?                 → get_time({})                  → "현재 시간은 20:07:05입니다."
```
**날씨는 일부러 도구가 없는 질문이다** — LLM이 있는 도구(hello/get_date/get_time) 중 아무거나
억지로 불러 지어내지 않고, "그런 기능이 없다"고 정직하게 답하는 걸 실측으로 확인할 수 있다.

## 실행
```bash
pip install mcp
cd 5.mcp/1.basic/1.intro
python 4.hello_client.py        # 3.hello_server 를 자동으로 띄워 호출 (LLM 불필요)
```

## 다음 단계

- **[`../2.protocol_deep/`](../2.protocol_deep/)** — 프로토콜 더 깊게: 도구 여러 개·resource·prompt 발견,
  **`debug_proxy` 로 오가는 JSON-RPC 들여다보기**, tool vs resource
- **[`../3.transports_http/`](../3.transports_http/)** — stdio → HTTP(streamable-http) 전송 차이
- LLM 이 MCP 도구를 **자동 호출**하게 하려면 → [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)(어댑터) 또는 [`../../2.openai/`](../../2.openai/)
