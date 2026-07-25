# Claude Code + MCP 운영 가이드

Claude Code(클라이언트) 쪽에서 **MCP 서버를 확인·등록·인증·재연결**하는 실무 정리.
(서버를 만드는 법이 아니라, 이미 있는 서버를 클라이언트에 붙이고 관리하는 법.)

> 표시 상태 기호: `✔ Connected` / `! Needs authentication` / `⏸ Pending approval`(승인 안 한 `.mcp.json` 서버)


============================================================
## 1. MCP 서버의 "출처"는 여러 갈래다  (가장 중요)
============================================================

한 목록에 떠도 **어디서 온 서버인지**가 다르다. `claude mcp get <이름>` 의 `Scope` 로 구분된다.

| 출처(Scope) | 저장 위치 | 등록 방법 | 예시 |
|------|-----------|-----------|------|
| **claude.ai config** | **claude.ai 계정(클라우드)** | claude.ai 웹 → Connectors | `claude.ai PlayMCP`, `claude.ai Gmail` … (이름에 `claude.ai ` 접두사) |
| **project** | 프로젝트 루트 **`.mcp.json`** (커밋됨) | 그 폴더에서 `claude` 실행 + 승인 | 우리 `sql-helper` / `dev-helper` |
| **local** | `~/.claude.json` (내 프로젝트별) | `claude mcp add` (기본) | 개인용 로컬 서버 |
| **user** | `~/.claude.json` (전역) | `claude mcp add --scope user` | 어디서나 쓰는 개인 서버 |
| enterprise | 조직 관리 정책 | 관리자 배포 | 사내 표준 서버 |

- **핵심**: `claude.ai ...` 접두사가 붙은 건 **웹에서 켠 계정 커넥터**다. 로컬 파일/이 레포와 무관.
- 우리가 만든 서버는 **project(`.mcp.json`)** 또는 **local(`claude mcp add`)** 로 들어가고, 이 목록에 **따로** 뜬다.


============================================================
## 2. 클라이언트별 설정 파일 — 통합 규격은 없다
============================================================

MCP 는 "설정 파일 위치·형식" 을 표준화하지 않는다. **클라이언트마다 자기 파일**을 읽는다.
그래서 `.vscode/mcp.json` 하나로 모든 클라이언트가 자동 인식되는 일은 **없다.**

| 클라이언트 | 설정 파일 | 자동 인식 트리거 |
|-----------|-----------|------------------|
| VSCode Copilot | `.vscode/mcp.json` | 그 폴더를 **Open Folder** |
| **Claude Code** | **`.mcp.json`**(프로젝트) / `~/.claude.json`(유저·로컬) | 그 폴더에서 **`claude` 실행**(cwd) / `claude mcp add` |
| Cursor | `.cursor/mcp.json` | 그 폴더를 열면 |
| Claude Desktop | `claude_desktop_config.json` | 앱 재시작 |
| Cline / Continue | `cline_mcp_settings.json` / `config.yaml` | 확장 전역 설정 |

- ⚠️ `.claude.json` 은 **홈의 유저 전역** 파일(폴더에 두는 게 아님). 폴더에 두는 프로젝트 설정은 **`.mcp.json`**.
- **VSCode = "폴더를 연다"**, **Claude Code = "그 폴더에서 실행한다(cwd)"** 가 트리거.
- ⚠️ Claude Code 는 **실행한 디렉토리(프로젝트 루트)의 `.mcp.json` 만** 읽는다 — **서브폴더 재귀 탐색 안 함.**
  레포 루트에서 `claude` 를 켜면 `.../2.sql_helpers/.mcp.json` 은 안 잡힌다 → 그 폴더로 `cd` 후 실행하거나, 레포 루트 `.mcp.json` 사용, 또는 `claude mcp add`.


============================================================
## 3. 상태 보기 —  `mcp status` 명령은 없다
============================================================

전용 `status` 서브명령은 **없다.** `list` 가 그 역할(헬스체크 포함)을 한다.

```bash
claude mcp list            # ★ 사실상 status — 서버별 ✔/!/⏸ 표시 (실행 시 헬스체크)
claude mcp get "<이름>"     # 한 서버 상세 (Scope + Status)
```
대화형(진짜 터미널)에서는:
```
/mcp                       # 라이브 패널: 상태 + 각 서버의 도구 목록 + 재인증 버튼
```
> ⚠️ VSCode 확장/SDK 안의 `/mcp` 는 **요약만** 준다("Use `/mcp` in the terminal for details").
> 서버별 **도구 목록**까지 보려면 **진짜 터미널에서 인자 없이 `/mcp`**.

- "설정(목록)" 과 "연결 상태" 는 별개:
  - 목록/설정 → 계정·파일에서 가져옴.
  - 상태(✔/!) → `list`/`/mcp` 할 때마다 **각 서버 URL 에 라이브 접속**해 확인. 그래서 토큰 만료되면 즉시 `! Needs authentication`.


============================================================
## 4. `claude mcp` 서브명령 전체
============================================================

```
add                       # 서버 추가:  claude mcp add <이름> -- <command> <args>
                          #   HTTP:     claude mcp add --transport http <이름> <URL> --header "Authorization: Bearer ..."
                          #   env 주입:  claude mcp add <이름> -e KEY=val -- <command>
add-json                  # JSON 문자열로 추가
add-from-claude-desktop   # Claude Desktop 설정 가져오기 (Mac/WSL)
get <이름>                # 상세 (Scope/Status). ※ 정확한 전체 이름 필요
list                      # 목록 + 상태
login <이름>              # 인증 (HTTP/SSE/claude.ai 커넥터) — 브라우저 OAuth
logout <이름>             # 저장된 OAuth 자격증명 제거
remove <이름>             # 삭제
```


============================================================
## 5. 이름 규칙 함정  (get/login/remove 가 "No MCP server" 날 때)
============================================================

`claude mcp get playmcp` → **실패.** 실제 이름은 **`claude.ai PlayMCP`** (접두사 + 공백 포함).

```bash
claude mcp get "claude.ai PlayMCP"        # ✅ 전체 이름 + 따옴표
claude mcp get "claude.ai Google Drive"
```
- **접두사 필수**: `claude.ai ` 까지 (`PlayMCP` 만으론 안 됨)
- **공백 → 따옴표 필수**: 안 감싸면 두 인자로 쪼개져 실패
- **대소문자 정확히**
- 실패해도 에러 메시지가 **정확한 이름 목록**을 알려주니 그걸 복사해 쓰면 된다.


============================================================
## 6. 인증(login)과 재연결(reconnect)
      — 다른 창에서 로그인하면 원래 창도 되나?
============================================================

미인증(`! Needs authentication`) 커넥터를 다른 터미널에서 로그인하면 **자격증명은 공유 저장(계정/디스크)** 되지만,
**이미 떠 있는 창은 자동 반영되지 않는다.** 한 번 재연결시켜야 한다.

```
[창 A] Claude Code 실행 중 (Gmail = ! Needs authentication)
   │
[창 B] 새 터미널  →  claude mcp login "claude.ai Gmail"
   │               (브라우저 OAuth 완료 → 자격증명 저장)
   ▼
[창 A]  →  /mcp reconnect all            (또는  /mcp reconnect "claude.ai Gmail")
   →  ✔ Connected 로 갱신
```

| 질문 | 답 |
|------|-----|
| 다른 창 login 이 저장되나? | ✅ 공유 저장/계정 → 새 세션은 자동 인증 |
| 원래 창이 **자동** 인증되나? | ❌ 실행 중 세션은 반영 안 됨 |
| 원래 창 반영 방법 | `/mcp reconnect all` 또는 창 재시작 |

- ⚠️ `claude mcp login` 은 브라우저 OAuth → **대화형 터미널**에서만. (VSCode 확장/비대화형 세션에선 못 돌림.)
- 재연결 안 먹으면 그냥 **창 재시작**(새 세션은 저장된 자격증명을 읽음).


============================================================
## 7. claude.ai 커넥터는 어디에 저장되나 (로컬 vs 클라우드)
============================================================

`claude.ai ...` 커넥터의 **실제 설정(URL·OAuth)은 로컬에 저장되지 않는다.** `~/.claude.json` 엔 두 가지만:

```
oauthAccount             : { accountUuid, emailAddress, ... }   # 계정 로그인(누구 커넥터를 가져올지)
claudeAiMcpEverConnected : [ ... "PlayMCP" ... ]                # "연결된 적 있음" 마커(이름만)
```

- 즉 **원본은 claude.ai 계정(클라우드)**, 로컬엔 로그인 + 마커만.
- 로그인하면 계정에서 **커넥터 목록을 받아와 메모리에 로드** → "로컬에 재설정" 이 아니라 "웹에서 가져와 올림".
- 그래서 계정 전역: 이 계정으로 쓰는 Claude 어디서나(재연결/재시작 후) 공유됨.
- 미인증 커넥터 재인증도 **claude.ai Connectors** 또는 `claude mcp login` 으로.


============================================================
## 8. 우리 서버(sql-helper 등)를 Claude Code 에 붙이기 — 요약
============================================================

```powershell
# (A) 그 폴더에서 자동 인식 — .mcp.json 이용
cd 8.mcp\5.vscode\2.sql_helpers
python init_db.py                 # sql-helper 는 DB 먼저
claude                            # 이 폴더에서 실행 → .mcp.json 발견 → 첫 사용 시 신뢰 승인

# (B) 폴더 무관하게 등록 — 절대경로
claude mcp add sql-helper -- "C:\...\.venv\Scripts\python.exe" "C:\...\2.sql_helpers\server.py"
claude mcp list                   # ✓ Connected 확인
```
- 등록 직후엔 `⏸ Pending approval`(project `.mcp.json`) 일 수 있음 → 승인하면 연결.
- `python` 은 **mcp 깔린 venv** 여야 함. 상대경로 `server.py` 는 그 폴더에서 실행할 때만 맞음.


============================================================
## 9. MCP 등록 vs 직접 설치(Bash) — "MCP 없이도 되던데?" 의 정체
============================================================

Claude Code 가 웹·브라우저·외부 작업을 하는 길은 **세 가지**다. **`claude mcp list` 에 뜨는 건 오직 3번(MCP)뿐**이라, 1·2번으로 한 일은 목록에 없어도 잘 돌아간다.

| 방법 | 무엇 | `claude mcp list` | 예 |
|------|------|:---:|----|
| **① 내장 도구** | Claude Code 자체 기능 | ❌ 안 뜸 | `WebFetch`(URL 읽기) · `WebSearch` · `Bash`+`curl`(내 서버 HTTP 호출) · `Read`/`Grep` |
| **② Bash 로 직접 설치·실행** | 내가 그때그때 라이브러리를 깔고 스크립트를 짜서 돌림 | ❌ 안 뜸 | `pip install playwright && playwright install` → 스크립트 실행 (`.playwright`·브라우저 캐시 생성) |
| **③ MCP 등록** | 미리 만들어진 도구 서버를 등록해 표준 방식으로 재사용 | ✅ 뜸(`mcp__…`) | `claude mcp add playwright -- npx @playwright/mcp@latest` |

> "MCP 목록에 없는데 브라우저를 알아서 깔고 실행하더라" = **②번**이다. MCP 가 아니라 **`Bash` 로 Playwright 를 직접 설치·스크립트**한 것. 그래서 `.playwright` 폴더가 생기고, 목록엔 안 뜬다.

### `pip install playwright` (②) vs `claude mcp add playwright` (③)

| | ② `pip install playwright` + 스크립트 | ③ `claude mcp add playwright` (MCP) |
|---|---|---|
| 정체 | Playwright 를 **일반 라이브러리**로 씀 | Playwright 를 **MCP 도구 서버**로 등록 |
| 도구 | **매번 내가 스크립트 작성** (page.click 등) | **미리 만든 40+ 도구** (`browser_click`·`browser_snapshot`…) 바로 호출 |
| 방식 | 내 코드가 브라우저 제어 | 접근성 트리 스냅샷(토큰 효율·결정적, 비전 불필요) |
| 재사용 | 그때그때 (일회성) | 한 번 등록 → 표준 방식 재사용·일관 |
| 목록 표시 | ❌ | ✅ `claude mcp list` |
| 적합 | 가끔/일회성 브라우저 작업 | 자주·반복 브라우저 작업 |

**언제 뭘:**
- **가끔** 브라우저 작업 → 굳이 등록 X, ②(Bash 즉석)로 충분.
- **자주·반복** → ③ 등록 권장. 특히 `--scope user` 로 모든 프로젝트에서:
  `claude mcp add --scope user playwright -- npx @playwright/mcp@latest`
- ③은 첫 실행 때 브라우저 바이너리(수백 MB) 다운로드, **실행 중 세션엔 재시작 후 반영**.

> **핵심:** MCP 는 "내장으로 안 되거나, 매번 직접 짜기 번거로운 능력"을 **표준 도구로 붙이는** 것이다.
> 브라우저 조작 자체는 ②(Bash 직접)로도 되지만, ③(MCP)은 **미리 만든 도구를 재사용**해 더 빠르고 일관적이다.

---
관련: 등록법 상세 [`5.vscode/1.dev_helpers/README.md`](5.vscode/1.dev_helpers/README.md) · 폴더 개요 [`5.vscode/README.md`](5.vscode/README.md)
