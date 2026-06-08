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
  - `1.intro/` — MCP 첫 접촉: SDK 확인 + hello 서버/클라이언트(첫 왕복). 상세: [`1.intro/README.md`](1.common/1.intro/README.md)
  - `2.protocol_deep/` — 프로토콜 깊게: 도구·resource·prompt 발견 + `debug_proxy` 로 JSON-RPC 보기 + tool vs resource
  - `3.transports/` — stdio vs HTTP 전송
- **2.openai** — `1.agent_tool/`, `2.multi_tools/` (각 폴더: 공통 서버 + manual 클라이언트 → GPT 클라이언트 빌드업)
- **3.anthropic** — `1.claude_desktop/` (Hello, 네트워크 서버, 파일 컨버터 등 Claude Desktop 등록용)
- **4.langchain** — `1.quickstart/`(adapters 빠른 시작) · `2.langchain_agent/` · `3.langchain_bridge/` · `4.tools_safety/`
- **5.vscode** — `server.py` + `.vscode/mcp.json` → VSCode 에서 내 도구 호출 (Copilot Agent Mode, 또는 Copilot 없이 Cline/Continue/Inspector)
- **9.projects** — `1.local/`(filesystem 서버·클라이언트) · `2.remote/`(원격) · `3.codebase_qa/`(**RAG 를 MCP 서버로 노출**, 멀티 클라이언트)

## 학습 단계 (쉬운 기초 → 응용)

> 처음이면 **1단계부터 순서대로**. 각 단계는 앞 단계를 전제로 한다.
> (폴더 번호는 "주제 분류", 아래 단계는 "학습 순서" — 둘이 항상 같진 않다.)

```
[1단계] MCP 프로토콜 그 자체 — LLM 없음                              난이도 ★
   1.common/1.intro            첫 왕복: hello 서버 + 클라이언트로 initialize→call_tool 를 '손으로'
   1.common/2.protocol_deep    프로토콜 깊게: 도구·resource·prompt 발견 + JSON-RPC 디버그
        ▼
[2단계] LLM 이 MCP 도구를 '자동' 호출                                난이도 ★★
   4.langchain/1.quickstart    langchain-mcp-adapters → 에이전트가 자동 호출 (가장 쉬움)
   2.openai/1.agent_tool       GPT function calling 으로 직접 (수동 → 자동 빌드업)
        ▼
[3단계] 전송 방식 · 멀티 서버                                        난이도 ★★
   1.common/3.transports       stdio → HTTP(streamable-http)
   2.openai/2.multi_tools      여러 MCP 서버를 한 클라이언트에서
        ▼
[4단계] LangChain 심화 (수동 변환 · 브릿지 · 안전성)                 난이도 ★★★
   4.langchain/2.langchain_agent → 3.langchain_bridge → 4.tools_safety
   (옛 문법 비교: 4.langchain/0.legacy(deprecated))
        ▼
[5단계] 실제 클라이언트에 붙이기 — 코드 없이 '설정'                  난이도 ★★
   3.anthropic/1.claude_desktop  Claude Desktop 에 내 서버 등록
   5.vscode                      VSCode(Copilot / Cline / Continue)에서 내 서버
        ▼
[6단계] 실전 응용 프로젝트                                           난이도 ★★★
   9.projects/1.local(filesystem) → 2.remote → 3.codebase_qa (RAG 를 MCP 로 노출)
```

> **빠른 길**: 코드보다 결과를 먼저 보고 싶으면 1단계 → 5단계(Claude Desktop/VSCode 설정) 로 건너뛰어도 된다.
> 같은 서버를 어디에 붙이든 동작하는 게 MCP 의 핵심이기 때문.

## 빠른 시작 관전 포인트 (`1.common`)

전체 관통 축: **수동→자동**(직접 호출 → LLM 자동), **내 서버→공식 서버**, **단일→혼합→멀티**.

| 파일 | 관전 포인트 |
|------|------------|
| `1.intro/3.hello_server.py` | `@mcp.tool()` 하나로 함수가 도구가 된다. **타입힌트+docstring 이 곧 LLM 이 읽는 명세**. stdio 단독 실행 시 입력 대기(정상) |
| `1.intro/4.hello_client.py` | MCP 핵심 동작 **`initialize → call_tool`** 을 손으로. 클라이언트가 서버를 자식 프로세스로 띄움 (아직 LLM 없음) |
| `2.protocol_deep/4.simple_client3_getinfo.py` | **`list_tools / list_resources / get_prompt`** — 서버가 가진 걸 전부 발견 |
| `2.protocol_deep/5.server_tools_resource.py` | **함수만 추가하면 도구가 늘어난다**. **tool(실행) vs resource(읽기 전용 데이터)** 차이 |

`4.langchain/1.quickstart` 관전 포인트:
| 파일 | 관전 포인트 |
|------|------------|
| `1.agent.py` | 같은 서버인데 **LLM 이 어떤 도구를 어떤 인자로 부를지 자동 결정**. `get_tools()` 가 손으로 하던 list_tools/call_tool 을 대신해준다 |
| `2.official_server.py` | **코드가 1.agent 와 거의 동일, `command` 가 python→npx 로 바뀐 것뿐** → "한 번 만든 서버는 어디서든 재사용" |
| `3.mcp_plus_local.py` | `mcp_tools + [내 @tool]` — 리스트만 합치면 끝 (둘 다 같은 BaseTool) |
| `4.multi_server.py` | 딕셔너리에 항목만 늘리면 멀티 서버 — `get_tools()` 가 모든 서버 도구를 합쳐준다 |

## 내 서버 테스트 방법

stdio 서버는 단독 실행하면 입력 대기로 멈춘다(고장 아님 — Ctrl+C). 클라이언트를 붙여서 테스트한다.

### A. 클라이언트로 호출 (간단, Node 불필요) ⭐
```bash
pip install mcp
cd "8.mcp/1.common/1.intro"
python 4.hello_client.py          # 기대: "Hello, John!" (3.hello_server 자동 실행)
# 더 깊게: cd ../2.protocol_deep && python 4.simple_client3_getinfo.py  (tools/resources/prompts 발견)
```

### B. MCP Inspector 로 클릭 테스트 (브라우저 UI, Node 필요)
```bash
pip install "mcp[cli]"                       # mcp CLI
cd "8.mcp/1.common/2.protocol_deep"
mcp dev 5.server_tools_resource.py           # 내부적으로 npx @modelcontextprotocol/inspector 실행 (Node 18+)
```
1. 터미널에 뜨는 **토큰이 포함된 URL** 을 그대로 브라우저에 연다(토큰 없이 열면 unauthorized).
2. **Connect** → 상태 Connected.
3. **Tools 탭 → List Tools → 도구 선택(예: `multiply`) → 인자 입력 → Run** → 결과 확인.
4. (resource 도 있으니) **Resources 탭 → List → `info://server`** 확인.
5. 끝낼 땐 터미널 **Ctrl+C**.

> 대안(설치 없이): `npx @modelcontextprotocol/inspector python 5.server_tools_resource.py`

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
