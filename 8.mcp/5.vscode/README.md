# 5.vscode — VSCode Copilot Agent Mode 에서 내 MCP 서버 쓰기

`1.common` 에서 만든 것과 똑같은 FastMCP 서버를, 이번엔 **클라이언트가 VSCode** 인 경우로 연결한다.
`.vscode/mcp.json` 으로 서버를 등록하면 **Copilot Chat 의 Agent Mode** 가 내 도구(`add`,
`word_count`, `to_snake_case`)를 직접 호출한다.

## 구성 파일
| 파일 | 설명 |
|------|------|
| `server.py` | dev-helper MCP 서버 (도구 3개 + resource) — 순수 파이썬 |
| `mcp.json.sample` | VSCode 등록 설정 **원본** (git 추적됨) |
| `.vscode/mcp.json` | 실제 활성 설정 — `.sample` 을 복사해 만든다 (`.vscode/` 는 레포에서 git 제외됨) |

> ⚠️ 레포 루트 `.gitignore` 가 `.vscode/` 를 제외하므로 활성 설정은 커밋되지 않는다.
> 그래서 `mcp.json.sample` 을 원본으로 두고, 각자 `.vscode/mcp.json` 으로 복사해 쓴다.
> (이 작업트리엔 이미 `.vscode/mcp.json` 이 있어 바로 동작한다. 새로 클론했다면 아래 1-b 참고.)

## 사전 준비
- VSCode **1.102 이상** + 확장: **GitHub Copilot**, **GitHub Copilot Chat**
- `pip install mcp`
- (서버 단독 점검 시) `pip install "mcp[cli]"` 후 `mcp dev server.py`

## 단계별 워크스루

1. **이 폴더를 연다** — VSCode `File ▸ Open Folder…` 로 `8.mcp/5.vscode` 를 연다.
   - `${workspaceFolder}` 가 이 폴더가 되어 `.vscode/mcp.json` 의 `server.py` 경로가 맞는다.
   - **1-b. 설정이 없으면 복사**: 새로 클론해 `.vscode/mcp.json` 이 없으면
     `cp mcp.json.sample .vscode/mcp.json` (PowerShell: `Copy-Item mcp.json.sample .vscode\mcp.json`).
   - (전체 레포를 열고 싶으면 이 내용을 레포 루트 `.vscode/mcp.json` 으로 옮기고
     경로를 `${workspaceFolder}/8.mcp/5.vscode/server.py` 로 바꾼다.)
2. **서버 시작** — `.vscode/mcp.json` 을 열면 `"dev-helper"` 항목 위에 **Start** 코드렌즈가 뜬다 → 클릭.
   - 또는 명령 팔레트(`Ctrl+Shift+P`) → **MCP: List Servers** → `dev-helper` → Start.
   - `python` 을 못 찾으면 `mcp.json` 의 `"command"` 를 venv python 절대경로로 바꾼다.
3. **Agent Mode 로 전환** — Copilot Chat 패널을 열고, 입력창 위 모드 선택을 **Agent** 로 바꾼다.
4. **도구 확인** — 채팅 입력창의 **도구(🛠) 아이콘** 클릭 → `dev-helper` 의 add / word_count /
   to_snake_case 가 보이는지 확인(체크).
5. **도구 호출** — 예시 프롬프트:
   ```
   to_snake_case 도구로 'myUserProfileName' 을 변환해줘.
   그리고 '오늘 날씨 정말 좋다' 가 몇 단어인지 word_count 로 세줘.
   ```
   → Copilot 이 도구를 호출하겠다고 표시하고(실행 전 **확인/허용** 프롬프트), 허용하면 결과를 보여준다.
6. **로그/관리** — 명령 팔레트의 **MCP: List Servers** 에서 재시작·로그 보기·중지.

## 동작 원리 (관전 포인트)
- VSCode 가 `mcp.json` 의 `command/args` 로 **server.py 를 자식 프로세스(stdio)로 띄운다** —
  `4.langchain/0.quickstart/1.agent.py` 가 `MultiServerMCPClient` 로 하던 것과 같은 일을 VSCode 가 한다.
- 즉 **서버 코드는 그대로**, 클라이언트만 (raw → LangChain → VSCode) 바뀐다. 이것이 MCP 의 핵심 가치.

## 참고
- VSCode MCP 문서: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
- 같은 서버를 Claude Desktop 에 등록하려면 → [`../3.anthropic/1.claude_desktop/`](../3.anthropic/1.claude_desktop/)
