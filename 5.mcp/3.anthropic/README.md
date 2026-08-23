# 3.anthropic — Claude로 MCP 쓰기

Claude와 MCP를 잇는 두 가지 서로 다른 방법.

| 폴더 | 내용 | 방식 |
|---|---|---|
| [`1.claude_desktop/`](1.claude_desktop/) | **Claude Desktop 앱**에 내 서버 등록(설정 파일) | 코드 없이 '설정'만 |
| [`2.anthropic_api/`](2.anthropic_api/) | **Anthropic API**가 코드로 MCP 도구를 직접 호출 (`tool_use`) | 코드 — `2.openai/1.agent_tool/`과 대칭 구조 |

둘은 서로 대체재가 아니라 **다른 상황을 위한 것**이다 — Claude Desktop 등록은 "사람이 채팅창에서
쓰는" 시나리오, `anthropic_api`는 "내 애플리케이션 코드가 Claude를 백엔드로 돌리는" 시나리오다.

## 다음 단계
- LLM 없이 순수 MCP 프로토콜부터 → [`../1.basic/`](../1.basic/)
- 같은 서버를 OpenAI로 돌리는 비교 → [`../2.openai/`](../2.openai/)
- Claude Agent SDK(에이전틱 프레임워크) 쪽 Claude 활용은 `3.anthropic/11.agent_sdk/`(레포 최상위,
  이 `5.mcp` 폴더 밖) 참고 — 성격이 달라 여긴 MCP 프로토콜 자체에 집중한다.
