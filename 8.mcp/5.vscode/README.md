# 5.vscode — 내 MCP 서버를 실제 클라이언트(VSCode·Claude Code 등)에 붙이기

`1.common`~`4.langchain` 에서 배운 FastMCP 서버를, 이제 **실제 클라이언트에 등록해서** 쓴다.
서버 코드는 그대로 두고 **클라이언트(VSCode Copilot / Cline / Continue / Claude Code)만 바꿔 끼우는** 게 MCP 의 핵심 가치다.

## 하위 폴더

| 폴더 | 주제 | 서버 | 배우는 것 |
|------|------|------|-----------|
| [`1.dev_helpers/`](1.dev_helpers/) | **개발 유틸 도구** | `dev-helper` (add / word_count / to_snake_case) | 여러 클라이언트에 등록하는 법 (Copilot·Cline·Continue·**Claude Code CLI**) |
| [`2.sql_helpers/`](2.sql_helpers/) | **DB 를 자연어로 질의** | `sql-helper` (list_tables / describe_table / run_query …) | 내 DB 를 MCP 로 노출 → "자연어 → SQL → 결과". 단순·무인증(로컬 sqlite) |
| [`3.sql_helpers_auth/`](3.sql_helpers_auth/) | **DB MCP 의 인증 3모델** | 서버관리 / 사용자별 스코프 / 클라이언트 제공 | 자격증명은 누가 쥐나·사용자별 접근·혼동된 대리인 (각 케이스 실행 데모) |

> 처음이면 **1.dev_helpers 먼저** — "등록/호출/제거" 흐름을 장난감 도구로 익히고,
> **2.sql_helpers** 에서 DB 질의 서버(단순·무인증)를, **3.sql_helpers_auth** 에서 인증이 얽히는 실전 3모델을 본다.

## 공통 아이디어

```
[클라이언트]                          [MCP 서버]              [자원]
Copilot / Cline / Continue / Claude Code ──stdio──▶ server.py ──▶ 함수·DB·파일
       └ 자연어로 시키면 LLM 이 도구를 자동 호출
```

- 어떤 클라이언트든 `command`/`args` 로 **server.py 를 자식 프로세스(stdio)로 띄운다** — 등록 방식만 다르고 원리는 동일.
- 등록 형식 비교:
  - VSCode Copilot: `.vscode/mcp.json`
  - Cline/Continue: 확장 설정(JSON/YAML)
  - Claude Code: `claude mcp add <이름> -- <command> <args>`
  - Claude Desktop: [`../3.anthropic/1.claude_desktop/`](../3.anthropic/1.claude_desktop/)

## 참고
- 원격/멀티유저로 확장(인증·OAuth) → [`../9.projects/2.remote/2.oauth/`](../9.projects/2.remote/2.oauth/)
- VSCode(Copilot) MCP 문서: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
