"""
MCP (Model Context Protocol) — Anthropic 이 제안한 LLM ↔ 도구 표준 프로토콜.
이 예제: MCP 가 뭐고 왜 표준이 되어가는지 설명 (코드 없는 컨셉 정리).

배경
  - LangChain @tool 은 LangChain 안에서만 쓸 수 있는 도구 정의 방식
  - OpenAI function calling 은 OpenAI 모델 한정 포맷
  - 도구를 만드는 사람과 쓰는 사람이 같은 프레임워크 안에 있어야 했음

MCP 가 제안하는 것
  - 도구는 "MCP 서버" 라는 독립 프로세스로 띄움 (stdio / HTTP 로 통신)
  - 어떤 LLM 클라이언트든 (Claude Desktop, Cursor, LangChain, LlamaIndex 등)
    같은 MCP 서버를 표준 프로토콜로 호출 가능
  - 한 번 만들어두면 모든 곳에서 재사용

비유:
  USB 가 키보드/마우스/USB 메모리/프린터를 한 포트로 통일했듯이,
  MCP 는 도구 제공자 ↔ LLM 클라이언트 사이의 USB 가 되려는 것.

지금 (2025~) 사용 가능한 MCP 서버 예
  - filesystem    : 로컬 파일 읽기/쓰기
  - github        : 이슈/PR/리포지토리 조회
  - postgres      : SQL 쿼리
  - puppeteer     : 웹 자동화
  - brave-search  : 웹 검색
  - 그 외 수십 개 (https://github.com/modelcontextprotocol/servers)

LangChain 과의 연결
  - langchain-mcp-adapters 패키지가 MCP 서버 → LangChain Tool 자동 변환
  - 8.2 에서 실제 MCP 서버 붙여서 에이전트로 사용
"""

print("=" * 60)
print("MCP (Model Context Protocol) — 한 줄 요약")
print("=" * 60)
print()
print("  MCP = LLM 도구 제공자와 클라이언트 사이의 표준 프로토콜")
print()
print("  도구 제공자가 MCP 서버 한 번 만들면 →")
print("  Claude Desktop, Cursor, LangChain, LlamaIndex 어디서든 그대로 사용")
print()
print("=" * 60)
print("주요 MCP 서버 (즉시 사용 가능)")
print("=" * 60)

servers = [
    ("filesystem",     "로컬 파일 시스템 (읽기/쓰기)"),
    ("github",         "GitHub 이슈/PR/리포지토리"),
    ("postgres",       "PostgreSQL SQL 쿼리"),
    ("sqlite",         "SQLite DB 쿼리"),
    ("puppeteer",      "웹 브라우저 자동화"),
    ("brave-search",   "Brave 웹 검색"),
    ("memory",         "키-값 저장소"),
    ("slack",          "Slack 메시징"),
    ("google-drive",   "Google Drive"),
]
for name, desc in servers:
    print(f"  {name:15s} {desc}")

print()
print("=" * 60)
print("LangChain 에서 쓰려면 (8.2 에서 실습)")
print("=" * 60)
print("""
  pip install langchain-mcp-adapters

  from langchain_mcp_adapters.client import MultiServerMCPClient
  from langchain.agents import create_agent

  client = MultiServerMCPClient({
      "filesystem": {
          "command": "npx",
          "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
          "transport": "stdio",
      },
  })
  tools = await client.get_tools()    # MCP 도구 → LangChain Tool 로 자동 변환
  agent = create_agent(llm, tools)
""")
