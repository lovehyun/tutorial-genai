# MCP (Model Context Protocol)

MCP 는 LLM 클라이언트와 외부 도구·데이터를 잇는 **표준 프로토콜**이다. USB 가 주변기기를
한 포트로 통일했듯, MCP 는 "도구 제공자 ↔ LLM 클라이언트" 사이를 표준화한다. 한 번 만든
MCP 서버는 Claude Desktop, Cursor, VSCode, OpenAI 클라이언트, LangChain 등 어디서든 재사용된다.

## 서버 vs 클라이언트

- **MCP 서버**: 도구(tool)·리소스(resource)·프롬프트(prompt)를 제공하는 독립 프로세스다.
  예를 들어 `@mcp.tool()` 데코레이터로 파이썬 함수를 도구로 등록한다. 함수의 타입 힌트와
  docstring 이 그대로 도구 명세(JSON Schema)가 되어 클라이언트(LLM)에게 전달된다.
- **MCP 클라이언트**: 서버를 실행하고 그 도구를 호출하는 쪽이다. LLM 애플리케이션이
  클라이언트가 되어, 사용자의 질문을 보고 어떤 도구를 어떤 인자로 부를지 결정한다.

서버는 보통 단독 실행하면 입력 대기 상태로 멈춘다. 클라이언트가 서버를 자식 프로세스로
띄우고 표준 입출력(stdio)으로 통신하기 때문이다. 즉 클라이언트가 서버의 수명을 관리한다.

## 핵심 3동작

MCP 통신은 JSON-RPC 기반이며 핵심 흐름은 세 단계다.

1. **initialize**: 클라이언트와 서버가 프로토콜 버전·기능(capabilities)을 교환하며 세션을 연다.
2. **list_tools**: 서버가 제공하는 도구 목록과 각 도구의 입력 스키마를 받아온다.
3. **call_tool**: 도구 이름과 인자를 보내 실행하고, content 블록 리스트로 결과를 받는다.

## 전송 방식 (Transport)

- **stdio**: 가장 단순하다. 클라이언트가 서버를 자식 프로세스로 띄워 stdin/stdout 으로 통신한다.
  로컬 도구에 적합하다. 이때 서버는 stdout 에 `print()` 를 쓰면 안 된다 — stdout 이 프로토콜
  채널이라 메시지 프레이밍이 깨진다. 로그는 stderr 로 보낸다.
- **streamable-http**: 네트워크 너머의 원격 서버에 적합하다. 웹 서비스 백엔드에서 MCP 서버를
  HTTP 로 노출할 때 쓴다. (구형 `sse` 전송은 deprecated 되어 streamable-http 로 대체되었다.)

## 왜 표준인가

도구를 MCP 서버로 한 번 만들면 클라이언트만 바꿔 끼우면 된다. 같은 RAG 검색 서버를
GPT 에서도, Claude Desktop 에서도, VSCode 에서도 그대로 쓸 수 있다. 이 재사용성이 MCP 의 핵심 가치다.
