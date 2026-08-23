# 2.openai/3.codex_cli — OpenAI Codex CLI 에 MCP 서버 등록

**ChatGPT 데스크톱 앱이 아니라 [OpenAI Codex CLI](https://github.com/openai/codex)** (터미널 코딩
에이전트) 얘기다 — 이름이 헷갈리기 쉬워 폴더명을 `codex_cli`로 명확히 했다. `1.agent_tool`/
`2.multi_tools`가 "코드로 MCP 클라이언트를 직접 짜는" 법이었다면, 여기는 **이미 만들어진 클라이언트
(Codex CLI)에 내 서버를 설정으로 등록**하는 법이다 — `3.anthropic/1.claude_desktop`이 Claude
Desktop에 등록하는 것과 같은 성격, 대상만 다르다.

## 파일
- `1.hello_server_for_codex.py` — Codex CLI 에 등록할 최소 hello 서버(모듈 docstring에 전체 절차 포함)

## 절차 (파일 상단 docstring 요약)
```bash
# 1) 서버 실행 환경 준비
uv venv
uv pip install "mcp[cli]"

# 2) Codex CLI 설치
npm install -g @openai/codex
codex --version

# 3) 등록 (CLI 명령으로 한 번에)
codex mcp add hello -- uv run hello_server.py

# 4) 등록 확인
codex mcp list

# 5) Codex 실행 후 안에서
codex
/mcp   # 등록된 MCP 서버 목록 확인
```
수동으로 등록하려면 `~/.codex/config.toml`(Windows는 `%USERPROFILE%\.codex\config.toml`)에
`[mcp_servers.hello]` 섹션을 직접 추가한다 — 정확한 예시는 파일 상단 docstring 참고.

## 관전 포인트
- **서버 코드는 재사용, 등록 방식만 다름**: `3.anthropic/1.claude_desktop/1.mcp_hello/hello_server.py`와
  본질적으로 같은 hello 서버를 Claude Desktop 대신 Codex CLI에 등록하는 것뿐이다 — "같은 서버,
  다른 클라이언트"라는 MCP의 핵심을 다시 확인한다.
- Codex CLI는 `command`/`args`/`cwd`를 TOML로 설정한다 — Claude Desktop의 JSON 설정과 형식만
  다를 뿐 개념(실행 커맨드 + 인자)은 동일하다.

## 설치
```bash
pip install "mcp[cli]"
npm install -g @openai/codex
```
