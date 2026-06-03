# 5.vscode — VSCode 에서 내 MCP 서버 쓰기 (Copilot / Cline / Continue)

`1.common` 에서 만든 것과 똑같은 FastMCP 서버를, 이번엔 **클라이언트가 VSCode** 인 경우로 연결한다.
`.vscode/mcp.json` 으로 서버를 등록하면 **Copilot Chat 의 Agent Mode** 가 내 도구(`add`,
`word_count`, `to_snake_case`)를 직접 호출한다.

> ⚠️ VSCode **내장** MCP(아래 Agent Mode 워크스루)는 **GitHub Copilot Chat 전용**이다.
> Copilot 을 안 쓴다면 → 아래 **‘Copilot 없이 쓰는 법’** 으로 같은 `server.py` 를 그대로 쓸 수 있다.

## 구성 파일
| 파일 | 설명 |
|------|------|
| `server.py` | dev-helper MCP 서버 (도구 3개 + resource) — 순수 파이썬 |
| `.vscode/mcp.json` | VSCode 워크스페이스 MCP 등록 설정 (git 추적됨 — 클론하면 바로 동작) |

> 레포 루트 `.gitignore` 는 `.vscode/*` 를 무시하되 `mcp.json` / `settings.json` 만 예외로 추적한다.
> 그래서 이 설정은 커밋되어, **폴더만 열면 별도 복사 없이 바로** 인식된다.

## 사전 준비
- VSCode **1.102 이상**
- `pip install mcp`
- **GitHub Copilot** + **GitHub Copilot Chat** 확장 — *아래 Agent Mode 워크스루에만 필요* (Copilot 미사용 시 'Copilot 없이 쓰는 법' 으로)
- (서버 단독 점검 시) `pip install "mcp[cli]"` 후 `mcp dev server.py`

## 단계별 워크스루

1. **이 폴더를 연다** — VSCode `File ▸ Open Folder…` 로 `8.mcp/5.vscode` 를 연다.
   - `${workspaceFolder}` 가 이 폴더가 되어 `.vscode/mcp.json` 의 `server.py` 경로가 맞는다.
     (이 설정은 레포에 커밋돼 있어 복사 없이 바로 인식된다.)
   - (전체 레포를 열고 싶으면 레포 루트 `.vscode/mcp.json` 으로 옮기고
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

## Copilot 없이 쓰는 법

위 워크스루는 Copilot Chat(Agent Mode) 전용이다. Copilot 이 없어도 **같은 `server.py` 를**
아래 방법으로 쓸 수 있다 — MCP 서버는 클라이언트와 무관하기 때문이다.

### 1) 확장 없이 — Inspector (가장 간단, 항상 가능)
```bash
cd 8.mcp/5.vscode
pip install "mcp[cli]"
mcp dev server.py     # 브라우저 Inspector 에서 도구 클릭 호출 (add / word_count / to_snake_case)
```
LLM 에이전트로 붙이려면 `4.langchain/0.quickstart/1.agent.py` 의 `SERVER` 를 이 폴더 `server.py` 로
바꿔 실행하면 된다(터미널에서). → Copilot 불필요.

### 2) Cline 확장 (BYO API 키, 무료)
Cline 의 **Configure MCP Servers** → `cline_mcp_settings.json` 에 추가(서버는 **절대경로**):
```json
{
  "mcpServers": {
    "dev-helper": {
      "command": "python",
      "args": ["C:/ABSOLUTE/PATH/TO/tutorial-genai/8.mcp/5.vscode/server.py"]
    }
  }
}
```
형식이 Claude Desktop 설정과 동일하다 → [`../3.anthropic/1.claude_desktop/`](../3.anthropic/1.claude_desktop/) 의 샘플 재사용 가능.

### 3) Continue 확장 (오픈소스, 무료)
Continue 설정(`config.yaml`)의 `mcpServers` 에 stdio 서버로 등록:
```yaml
mcpServers:
  - name: dev-helper
    command: python
    args:
      - C:/ABSOLUTE/PATH/TO/tutorial-genai/8.mcp/5.vscode/server.py
```

> 어느 쪽이든 핵심은 같다 — `command/args` 로 `server.py` 를 stdio 로 띄우는 것.
> Cline/Continue 설정은 확장의 **전역 저장소**(워크스페이스 밖)에 저장되어 레포에는 커밋되지 않는다.
> 그래서 이 폴더의 `.vscode/mcp.json`(Copilot용)과 달리, 위 설정은 각자 환경에 직접 넣는다.

## 동작 원리 (관전 포인트)
- VSCode 가 `mcp.json` 의 `command/args` 로 **server.py 를 자식 프로세스(stdio)로 띄운다** —
  `4.langchain/0.quickstart/1.agent.py` 가 `MultiServerMCPClient` 로 하던 것과 같은 일을 VSCode 가 한다.
- 즉 **서버 코드는 그대로**, 클라이언트만 (raw → LangChain → VSCode) 바뀐다. 이것이 MCP 의 핵심 가치.

## 참고
- VSCode(Copilot) MCP 문서: <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
- Cline MCP: <https://docs.cline.bot/mcp/configuring-mcp-servers> · Continue MCP: <https://docs.continue.dev/customize/deep-dives/mcp>
- 같은 서버를 Claude Desktop 에 등록하려면 → [`../3.anthropic/1.claude_desktop/`](../3.anthropic/1.claude_desktop/)
