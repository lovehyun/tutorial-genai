# 1.common/1.intro — MCP 첫 접촉 (LLM 없이)

MCP 를 **가장 처음** 만나는 곳. SDK 를 확인하고, `@mcp.tool()` 하나짜리 서버를 만들어
클라이언트로 **첫 왕복**(initialize → call_tool)을 해본다. 아직 LLM 은 없다.

> 서버는 단독 실행하면 stdin 대기로 멈춘다(고장 아님). **클라이언트가 서버를 자식 프로세스로 띄운다.**

## 학습 순서

| 단계 | 파일 | 무엇을 보나 |
|---|---|---|
| 0 | `0.asyncio_eventloop/` | (선행) MCP 가 왜 async 인지 — 이벤트 루프 기초 |
| 1 | `1.mcp_version.py` | 설치된 `mcp` SDK 버전 확인 |
| 2 | `2.mcp_docs.py` | SDK 구조 둘러보기 (FastMCP / ClientSession 등) |
| 3 | `3.hello_server.py` | `@mcp.tool()` 하나로 첫 MCP 서버 (`say_hello`) |
| 4 | `4.hello_client.py` | 그 서버에 붙어 `call_tool("say_hello")` — **첫 왕복** |

## 실행
```bash
pip install mcp
cd 8.mcp/1.common/1.intro
python 4.hello_client.py        # 3.hello_server 를 자동으로 띄워 호출 (LLM 불필요)
```

## 다음 단계

- **[`../2.protocol_deep/`](../2.protocol_deep/)** — 프로토콜 더 깊게: 도구 여러 개·resource·prompt 발견,
  **`debug_proxy` 로 오가는 JSON-RPC 들여다보기**, tool vs resource
- **[`../3.transports/`](../3.transports/)** — stdio → HTTP(streamable-http) 전송 차이
- LLM 이 MCP 도구를 **자동 호출**하게 하려면 → [`../../4.langchain/1.quickstart/`](../../4.langchain/1.quickstart/)(어댑터) 또는 [`../../2.openai/`](../../2.openai/)
