# 8.mcp — Model Context Protocol

> **MCP (Model Context Protocol)** = Anthropic 이 제안한 LLM ↔ 도구 표준 프로토콜.
> 도구를 "MCP 서버" 라는 독립 프로세스로 만들면, 어떤 LLM 클라이언트(Claude Desktop,
> Cursor, VSCode, OpenAI 클라이언트, LangChain …)에서든 같은 서버를 표준 방식으로 재사용한다.
>
> 비유: USB 가 키보드·마우스·메모리·프린터를 한 포트로 통일했듯이, MCP 는
> 도구 제공자 ↔ LLM 클라이언트 사이의 USB 가 되려는 것.

이 폴더는 **provider/framework 중립**으로 MCP 를 다룬다. (원래 `4.anthropic/3.mcp` 와
`2.langchain/8.agents/8.mcp` 에 흩어져 있던 것을 여기로 통합했다.)

## 디렉토리 구조

| 폴더 | 내용 | LLM/Node |
|------|------|----------|
| [`1.common/`](1.common/) | **공통(중립): MCP 그 자체** — 서버 만들기, 순수 클라이언트, 전송(stdio/HTTP) | 없음 |
| [`2.openai/`](2.openai/) | GPT 로 MCP 도구 호출 (agent_tool, multi_tools) | OpenAI |
| [`3.anthropic/`](3.anthropic/) | Claude API + **Claude Desktop** 연동 | Claude |
| [`4.langchain/`](4.langchain/) | `langchain-mcp-adapters` · LangGraph 브릿지 · 도구 안전성 | OpenAI |
| [`5.vscode/`](5.vscode/) | **VSCode 연동** (`.vscode/mcp.json` + Copilot agent mode) | VSCode |
| [`9.projects/`](9.projects/) | 실전 프로젝트 (filesystem, remote, codebase-QA) | 혼합 |

### 각 폴더 안

- **1.common**
  - `1.intro/` — hello/simple 서버·클라이언트, asyncio 기초, FileSystem/Gmail 서버 문서
  - `2.server_quickstart/` — FastMCP 로 내 서버 만들기 → 순수 클라이언트 → 도구·resource 확장 (가장 깔끔한 입문)
  - `3.transports/` — stdio vs HTTP 전송
- **2.openai** — `1.agent_tool/`, `2.multi_tools/` (각 폴더: 공통 서버 + manual 클라이언트 → GPT 클라이언트 빌드업)
- **3.anthropic** — `1.claude_desktop/` (Hello, 네트워크 서버, 파일 컨버터 등 Claude Desktop 등록용)
- **4.langchain** — `1.quickstart/`(adapters 빠른 시작) · `2.langchain_agent/` · `3.langchain_bridge/` · `4.tools_safety/`
- **5.vscode** — `server.py` + `.vscode/mcp.json` → VSCode 에서 내 도구 호출 (Copilot Agent Mode, 또는 Copilot 없이 Cline/Continue/Inspector)
- **9.projects** — `1.local/`(filesystem 서버·클라이언트) · `2.remote/`(원격) · `3.codebase_qa/`(**RAG 를 MCP 서버로 노출**, 멀티 클라이언트)

## 학습 순서 (추천)

```
1.common/2.server_quickstart   내 서버가 동작 → 순수 클라이언트로 호출 → 도구 확장
        │  (프로토콜 원리: initialize → list_tools → call_tool 를 눈으로)
        ▼
4.langchain/1.quickstart       langchain-mcp-adapters 로 에이전트가 자동 호출
        │  또는 2.openai (GPT 직접) / 3.anthropic (Claude Desktop)
        ▼
1.common/3.transports          stdio → HTTP 전송 차이
        ▼
9.projects                     filesystem / remote / codebase-QA 실전
        ▼
5.vscode                       VSCode Copilot agent mode 에서 내 MCP 서버 사용
```

## 빠른 시작 관전 포인트 (`1.common/2.server_quickstart`)

전체 관통 축: **수동→자동**(직접 호출 → LLM 자동), **내 서버→공식 서버**, **단일→혼합→멀티**.

| 파일 | 관전 포인트 |
|------|------------|
| `1.server_minimal.py` | `@mcp.tool()` 하나로 함수가 도구가 된다. **타입힌트+docstring 이 곧 LLM 이 읽는 명세**. `mcp.run()` 기본 stdio → 단독 실행 시 입력 대기로 멈춤(정상) |
| `2.client_raw.py` | MCP 의 3동작 **`initialize → list_tools → call_tool`**. 클라이언트가 서버를 자식 프로세스로 띄움. 결과는 content 블록 리스트. (아직 LLM 없음 — 손으로 호출) |
| `3.server_tools_resource.py` | **함수만 추가하면 도구가 늘어난다**(서버만 바뀌고 사용처는 그대로). **tool(실행) vs resource(읽기 전용 데이터)** 차이 |

`4.langchain/1.quickstart` 관전 포인트:
| 파일 | 관전 포인트 |
|------|------------|
| `1.agent.py` | 같은 서버인데 **LLM 이 어떤 도구를 어떤 인자로 부를지 자동 결정**. `get_tools()` 가 2.client_raw 의 수동 과정을 대신해준다 |
| `2.official_server.py` | **코드가 1.agent 와 거의 동일, `command` 가 python→npx 로 바뀐 것뿐** → "한 번 만든 서버는 어디서든 재사용" |
| `3.mcp_plus_local.py` | `mcp_tools + [내 @tool]` — 리스트만 합치면 끝 (둘 다 같은 BaseTool) |
| `4.multi_server.py` | 딕셔너리에 항목만 늘리면 멀티 서버 — `get_tools()` 가 모든 서버 도구를 합쳐준다 |

## 내 서버 테스트 방법

`1.server_minimal.py` 는 stdio 서버라 단독 실행하면 입력 대기로 멈춘다(고장 아님 — Ctrl+C). 클라이언트를 붙여서 테스트한다.

### A. 클라이언트로 호출 (간단, Node 불필요) ⭐
```bash
pip install mcp
cd "8.mcp/1.common/2.server_quickstart"
python 2.client_raw.py
# 기대: "add: ..." 도구 목록 + "add(3, 5) = 8"
```

### B. MCP Inspector 로 클릭 테스트 (브라우저 UI, Node 필요)
```bash
pip install "mcp[cli]"                       # mcp CLI
cd "8.mcp/1.common/2.server_quickstart"
mcp dev 3.server_tools_resource.py           # 내부적으로 npx @modelcontextprotocol/inspector 실행 (Node 18+)
```
1. 터미널에 뜨는 **토큰이 포함된 URL** 을 그대로 브라우저에 연다(토큰 없이 열면 unauthorized).
2. **Connect** → 상태 Connected.
3. **Tools 탭 → List Tools → 도구 선택(예: `multiply`) → 인자 입력 → Run** → 결과 확인.
4. (resource 도 있으니) **Resources 탭 → List → `info://server`** 확인.
5. 끝낼 땐 터미널 **Ctrl+C**.

> 대안(설치 없이): `npx @modelcontextprotocol/inspector python 3.server_tools_resource.py`

## 환경 설정

```bash
# 공통/LangChain (순수 파이썬)
pip install mcp langchain-mcp-adapters langchain-openai langgraph python-dotenv

# 공식 MCP 서버(filesystem 등) 실행용
node --version    # Node.js 18+ (npx)
```
`.env` 에 `OPENAI_API_KEY`(2.openai·4.langchain), `ANTHROPIC_API_KEY`(3.anthropic) 가 필요할 수 있다.

## 관련 커리큘럼 / 프로젝트
- `99.curriculums/3.advanced/1.mcp_protocol_deep_dive/` — MCP 3일 심화 과정
- `10.project/12.nas_mcp_agent/` — NAS 파일스캔 MCP 에이전트 실전 프로젝트

## 더 보기
- 공식 문서: <https://modelcontextprotocol.io/>
- 공식 서버 모음: <https://github.com/modelcontextprotocol/servers>
- 파이썬 SDK: <https://github.com/modelcontextprotocol/python-sdk>

---
> **둘러보기**: [`5.vscode/`](5.vscode/) — VSCode Copilot Agent Mode 연동 워크스루 ·
> [`9.projects/3.codebase_qa/`](9.projects/3.codebase_qa/) — RAG 를 MCP 서버로 노출(GPT·Claude·LangChain·VSCode 재사용).
