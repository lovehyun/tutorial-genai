# 5.vscode — 내 MCP 서버를 실제 클라이언트(VSCode·Claude Code 등)에 붙이기

`1.basic`~`4.langchain` 에서 배운 FastMCP 서버를, 이제 **실제 클라이언트에 등록해서** 쓴다.
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

## ⚙️ 클라이언트별 설정 파일 (여기가 핵심 — 통합 규격은 없다!)

**MCP 는 "설정 파일 위치·형식"을 표준화하지 않는다.** 클라이언트마다 자기 파일을 읽는다.
그래서 `.vscode/mcp.json` 하나로 모든 클라이언트가 자동 인식되는 일은 **없다.**

| 클라이언트 | 설정 파일 | 자동 인식 트리거 |
|-----------|-----------|------------------|
| **VSCode Copilot** | `.vscode/mcp.json` | 그 폴더를 **Open Folder** 하면 |
| **Claude Code** | **`.mcp.json`**(프로젝트) 또는 `~/.claude.json`(유저전역) | 그 폴더에서 **`claude` 실행**(cwd) / 또는 `claude mcp add` |
| Cursor | `.cursor/mcp.json` | 그 폴더를 열면 |
| Claude Desktop | `claude_desktop_config.json` | 앱 재시작 |
| Cline / Continue | `cline_mcp_settings.json` / `config.yaml` | 확장 전역 설정 |

> ⚠️ `.claude.json` 은 **홈의 유저 전역** 파일(폴더에 두는 게 아님). 폴더에 두는 프로젝트 설정은 **`.mcp.json`**.

**VSCode vs Claude Code 자동 인식의 차이:**
- VSCode = "그 폴더를 **연다**" → `.vscode/mcp.json` 발견.
- Claude Code = "그 폴더에서 **`claude` 를 실행**한다(cwd)" → `.mcp.json` 발견 (첫 사용 시 신뢰 승인).
  레포 루트에서 `claude` 를 켜면 **서브폴더의 `.mcp.json` 은 안 잡힌다** → 레포 루트 `.mcp.json` 을 쓰거나 `claude mcp add` 로 등록.

→ 그래서 `1.dev_helpers/` · `2.sql_helpers/` 에는 **두 파일을 다 넣어뒀다**: `.vscode/mcp.json`(VSCode) + `.mcp.json`(Claude Code).
그 폴더를 VSCode 로 열거나, 그 폴더에서 `claude` 를 실행하면 각각 자동 인식된다.
(둘 다 `python server.py` 를 상대경로로 띄우므로, `python` 이 mcp 깔린 venv 여야 하고 그 폴더가 실행 기준이어야 한다. 2.sql_helpers 는 먼저 `python init_db.py`.)

- Claude Code 수동 등록(폴더 무관): `claude mcp add <이름> -- <python 절대경로> <server.py 절대경로>` (→ [`1.dev_helpers/README.md`](1.dev_helpers/README.md))

## 📎 Claude Code 로 MCP 서버 다루기 (운영 가이드)

서버 확인·설정 출처·상태·**인증(login)·재연결(reconnect)**, `claude mcp` 명령, claude.ai 커넥터가
어디 저장되는지 등 **클라이언트 운영 지식**은 별도 문서로 정리했다 (섹션별 `====` 구분):

→ **[`claude_code_mcp_guide.md`](../claude_code_mcp_guide.md)**

핵심만:
- MCP 서버는 **출처가 여러 갈래** — `claude.ai 커넥터`(웹/계정) vs `project(.mcp.json)` vs `local/user(claude mcp add)`.
- 상태 = `claude mcp list` (`mcp status` 명령은 없음). 상세 = `claude mcp get "정확한 전체 이름"`.
- 미인증 커넥터: 다른 터미널에서 `claude mcp login "<이름>"` → 원래 창에서 `/mcp reconnect all`.

## 참고
- 원격/멀티유저로 확장(인증·OAuth) → [`../9.projects/2.remote/2.oauth/`](../9.projects/2.remote/2.oauth/)
- VSCode(Copilot) MCP 문서: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
