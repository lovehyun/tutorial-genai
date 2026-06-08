# 1.common — MCP 그 자체 (LLM 없이)

MCP를 **밑바닥부터** 본다. LLM·프레임워크 없이, 서버를 만들고 클라이언트가 직접 호출하며
"프로토콜이 무엇인지"를 눈으로 익힌다.

| 폴더 | 내용 | 전송 |
|---|---|---|
| [`1.intro/`](1.intro/) | 첫 접촉 — SDK 확인 + hello 서버/클라이언트(첫 왕복) | stdio |
| [`2.protocol_deep/`](2.protocol_deep/) | 도구 여러 개·**resource·prompt 발견**·`debug_proxy`로 JSON-RPC 보기 | stdio |
| [`3.transports/`](3.transports/) | stdio ↔ HTTP(streamable-http) 차이 | HTTP |

## MCP 서버가 제공하는 3가지 (핵심 개념)

MCP 서버는 클라이언트(LLM)에게 **3종류**를 제공한다. 클라이언트는 각각 `list_*`로 발견하고 호출한다.

| 종류 | 무엇인가 | 서버 정의 | 클라이언트 사용 | 비유 |
|---|---|---|---|---|
| **tool** | 모델이 **실행**하는 동작(함수). 계산·부작용 O | `@mcp.tool()` | `list_tools()` → `call_tool(name, args)` | 함수 호출 |
| **resource** | 모델이 **읽는** 데이터. URI로 식별, 읽기 전용 | `@mcp.resource("info://x")` | `list_resources()` → `read_resource(uri)` | 파일/GET |
| **prompt** | 재사용 **프롬프트 템플릿**(서버가 제공) | `@mcp.prompt()` | `list_prompts()` → `get_prompt(name, args)` | 지시문 양식 |

```python
# 서버 (FastMCP)                         # 클라이언트 (ClientSession)
@mcp.tool()                              tools = (await session.list_tools()).tools
def add(a: int, b: int) -> int: ...      await session.call_tool("add", {"a": 3, "b": 5})

@mcp.resource("info://server")           await session.read_resource("info://server")
def server_info() -> str: ...

@mcp.prompt()                            await session.get_prompt("translate", {...})
def translate(text, lang) -> str: ...
```

→ tool/resource/prompt를 **한 번에 발견**하는 예제: [`2.protocol_deep/4.simple_client3_getinfo.py`](2.protocol_deep/),
  tool vs resource 비교: [`2.protocol_deep/5·6`](2.protocol_deep/).

## 관전 포인트
- **타입힌트 + docstring 이 곧 LLM이 읽는 도구 명세**가 된다 (FastMCP가 JSON Schema 자동 생성).
- 클라이언트가 **서버를 자식 프로세스(stdio)로 띄운다** → 서버는 단독 실행 시 입력 대기로 멈춤(정상).
- MCP 핵심 흐름은 항상 **`initialize → list_tools → call_tool`** (전송이 stdio든 HTTP든 동일).
- 서버는 stdio에서 **stdout에 `print()` 금지**(JSON-RPC 채널 오염) — 로그는 stderr로.

## 다음 단계
LLM이 이 도구들을 **자동 호출**하게 → [`../4.langchain/1.quickstart/`](../4.langchain/)(어댑터) · [`../2.openai/`](../2.openai/)(GPT)
