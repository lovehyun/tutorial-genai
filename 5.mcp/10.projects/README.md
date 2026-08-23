# 10.projects — 실전 응용 프로젝트

지금까지 `1.basic`~`5.vscode`에서 배운 걸 실제로 쓸모 있는 형태로 조립한다. 난이도는 대체로
아래 순서로 올라간다.

| 폴더 | 내용 | 핵심 |
|---|---|---|
| [`1.local/`](1.local/) | 로컬 filesystem MCP 서버 + 클라이언트 | stdio, LLM 없음/단순 function calling |
| [`2.remote/`](2.remote/) | 원격 HTTP 서버 — `1.intro`(무인증) → `2.oauth`(**Bearer 인증**) | 전송 + 인증 |
| [`3.codebase_qa/`](3.codebase_qa/) | RAG를 MCP 서버로 노출 | `search`/`answer`, 의미 검색 |
| [`4.mini_context7/`](4.mini_context7/) | context7 스타일 `resolve→fetch` 2단계 문서 검색 | ID 기반 검색(임베딩 불필요) — `3`과 대비해서 볼 것 |
| [`5.chatbot_web/`](5.chatbot_web/) | Flask 웹 챗봇 + MCP(계산기·시간·주사위·날씨) | 서버 1개 + 웹앱 |
| [`6.multi_mcp_concierge/`](6.multi_mcp_concierge/) | 웹 챗봇이 **독립된 외부 MCP 서버 2개**에 동시 연결 | 서버 여러 개, 클라이언트 하나 |
| [`7.multi_vendor_capstone/`](7.multi_vendor_capstone/) | **서버 하나**를 OpenAI·Anthropic·LangChain 클라이언트가 동시에 사용 | 서버 하나, 클라이언트 벤더 여럿 — `6`의 반대 방향 |

## 관전 포인트
- **`3` vs `4`**: 둘 다 "문서를 찾아준다"지만 검색 방식이 다르다 — `3`은 임베딩 기반 의미 검색,
  `4`는 정확한 ID로 먼저 찾고 그 문서를 가져오는 방식(context7이 실제로 쓰는 패턴). 나란히
  비교하면 "언제 의미 검색이 필요하고 언제 필요 없는지"가 보인다.
- **`6` vs `7`**: MCP를 "서버 여러 개 ↔ 클라 하나"(`6`)로도, "서버 하나 ↔ 클라 벤더 여럿"(`7`)으로도
  쓸 수 있다는 걸 대비해서 보여준다 — 둘 다 "MCP로 조합이 자유롭다"는 같은 결론으로 수렴한다.

## 다음 단계
- `1.basic`부터 순서대로 보고 싶다면 → [`../1.basic/`](../1.basic/)
- 실제 클라이언트(Claude Desktop/VSCode)에 등록하는 법 → [`../3.anthropic/1.claude_desktop/`](../3.anthropic/1.claude_desktop/), [`../5.vscode/`](../5.vscode/)
