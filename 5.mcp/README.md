# 5.mcp — Model Context Protocol

> **MCP (Model Context Protocol)** = Anthropic 이 제안한 LLM ↔ 도구 표준 프로토콜.
> 도구를 "MCP 서버" 라는 독립 프로세스로 만들면, 어떤 LLM 클라이언트(Claude Desktop,
> Cursor, VSCode, OpenAI 클라이언트, LangChain …)에서든 같은 서버를 표준 방식으로 재사용한다.
>
> 비유: USB 가 키보드·마우스·메모리·프린터를 한 포트로 통일했듯이, MCP 는
> 도구 제공자 ↔ LLM 클라이언트 사이의 USB 가 되려는 것.

이 폴더는 **provider/framework 중립**으로 MCP 를 다룬다. (원래 `3.anthropic/3.mcp` 와
`2.langchain/8.agents/8.mcp` 에 흩어져 있던 것을 여기로 통합했다 — 지금은 둘 다 이 폴더로 완전히
이전됐고, 원래 있던 자리엔 흔적도 남아있지 않다.)

## 디렉토리 구조

| 폴더 | 내용 | LLM/Node |
|------|------|----------|
| [`1.basic/`](1.basic/) | **공통(중립): MCP 그 자체** — 서버 만들기, 순수 클라이언트, 전송(stdio/HTTP), 양방향 심화 | 없음 |
| [`2.openai/`](2.openai/) | GPT 로 MCP 도구 호출 (agent_tool, multi_tools) · Codex CLI 등록 | OpenAI |
| [`3.anthropic/`](3.anthropic/) | **Claude Desktop** 등록 + Claude API 직접 호출(`tool_use`) | Claude |
| [`4.langchain/`](4.langchain/) | `langchain-mcp-adapters` · LangGraph 브릿지 · 도구 안전성 | OpenAI |
| [`5.vscode/`](5.vscode/) | **실제 클라이언트에 등록** — `1.dev_helpers`(등록법) · `2.sql_helpers`(**DB 자연어 질의**) · `3.sql_helpers_auth`(**인증 3모델**) | VSCode·Claude Code |
| [`6.ollama/`](6.ollama/) | 로컬 모델(qwen2.5:7b)로 MCP 도구 호출 — API 키·인터넷 불필요, 완전 무료 | Ollama |
| `7~9` | *(예약)* — 다른 벤더/클라이언트(Gemini MCP 클라이언트 등)가 추가되면 이 번호대역에 들어간다 | — |
| [`10.projects/`](10.projects/) | 실전 프로젝트 (filesystem, remote, codebase-QA, 멀티벤더 캡스톤) | 혼합 |

### 각 폴더 안

- **1.basic**
  - `1.intro/` — MCP 첫 접촉: SDK 확인 + hello 서버/클라이언트(첫 왕복). 상세: [`1.intro/README.md`](1.basic/1.intro/README.md)
  - `2.protocol_deep/` — 프로토콜 깊게: 도구·resource·prompt 발견 + `debug_proxy` 로 JSON-RPC 보기 + tool vs resource
  - `3.transports_http/` — stdio vs HTTP 전송
  - `4.advanced/` — **양방향·Context 심화**: sampling / progress·logging / elicitation / roots. 상세: [`4.advanced/README.md`](1.basic/4.advanced/README.md)
- **2.openai** — `1.agent_tool/`, `2.multi_tools/` (각 폴더: 공통 서버 + manual 클라이언트 → GPT 클라이언트 빌드업) · `3.codex_cli/`(OpenAI Codex CLI 에 등록)
- **3.anthropic** — `1.claude_desktop/` (Hello, 네트워크 서버, 파일 컨버터 등 Claude Desktop 등록용) · `2.anthropic_api/`(**Claude API가 코드로 MCP 직접 호출** — `2.openai/1.agent_tool`과 대칭)
- **4.langchain** — `1.quickstart/`(adapters 빠른 시작) · `2.langchain_agent/` · `3.langchain_bridge/` · `4.tools_safety/` · `5.remote_http/`(**원격 HTTP 서버 + 실전 API(yfinance) 서버**) · `6.human_in_loop/`(**MCP 도구 실행 전 사람 승인**) · `7.guardrails/`(**인젝션·rm -rf·PII·악성 서버 차단**)
- **5.vscode** — 내 서버를 실제 클라이언트에 등록. `1.dev_helpers/`(dev-helper 도구를 Copilot·Cline·Continue·**Claude Code** 에 등록) · `2.sql_helpers/`(**내 DB 를 MCP 로 노출 → 자연어로 SQL 질의**, sqlite/postgres/mysql, 단순·무인증) · `3.sql_helpers_auth/`(**인증 3모델**: 서버관리 / 사용자별 스코프(HTTP+Bearer) / 클라이언트 제공 프록시)
- **6.ollama** — `1.agent_tool/`(`2.openai/1.agent_tool`, `3.anthropic/2.anthropic_api`와 대칭 — **로컬 모델**로 도구 자동 선택, API 키·인터넷 불필요)
- **10.projects** — `1.local/`(filesystem 서버·클라이언트) · `2.remote/`(원격: `1.intro` 무인증 → `2.oauth` **Bearer 인증**) · `3.codebase_qa/`(**RAG 를 MCP 서버로 노출**, 멀티 클라이언트) · `4.mini_context7/`(ID 기반 문서 검색) · `5.chatbot_web/`·`6.multi_mcp_concierge/`(웹 챗봇, 서버 여러 개) · `7.multi_vendor_capstone/`(**서버 하나를 OpenAI·Anthropic·LangChain 이 동시에** 사용). 상세: [`10.projects/README.md`](10.projects/README.md)

## 학습 단계 (쉬운 기초 → 응용)

> 처음이면 **1단계부터 순서대로**. 각 단계는 앞 단계를 전제로 한다.
> (폴더 번호는 "주제 분류", 아래 단계는 "학습 순서" — 둘이 항상 같진 않다.)

```
[1단계] MCP 프로토콜 그 자체 — LLM 없음                              난이도 ★
   1.basic/1.intro            첫 왕복: hello 서버 + 클라이언트로 initialize→call_tool 를 '손으로'
   1.basic/2.protocol_deep    프로토콜 깊게: 도구·resource·prompt 발견 + JSON-RPC 디버그
        ▼
[2단계] LLM 이 MCP 도구를 '자동' 호출                                난이도 ★★
   4.langchain/1.quickstart    langchain-mcp-adapters → 에이전트가 자동 호출 (가장 쉬움)
   2.openai/1.agent_tool       GPT function calling 으로 직접 (수동 → 자동 빌드업)
   3.anthropic/2.anthropic_api Claude tool_use 로 직접 (2.openai 와 대칭)
   6.ollama/1.agent_tool       로컬 모델로 직접 — API 키·인터넷 불필요
        ▼
[3단계] 전송 방식 · 멀티 서버                                        난이도 ★★
   1.basic/3.transports_http       stdio → HTTP(streamable-http)
   2.openai/2.multi_tools      여러 MCP 서버를 한 클라이언트에서
        ▼
[4단계] 양방향·Context 심화 (프로토콜의 나머지 절반)                 난이도 ★★★
   1.basic/4.advanced         sampling → progress·logging → elicitation → roots
   (서버가 되묻고, 진행률/로그를 흘리고, 사람에게 확인받고, 접근범위를 받는다)
        ▼
[5단계] LangChain 심화 (수동 변환 · 브릿지 · 안전성)                 난이도 ★★★
   4.langchain/2.langchain_agent → 3.langchain_bridge → 4.tools_safety
              → 5.remote_http → 6.human_in_loop → 7.guardrails
   (5.remote_http:   원격 HTTP 서버 + 실제 API 호출 서버 — 서버엔 LangChain 이 없다는 걸 확인)
   (6.human_in_loop: 되돌릴 수 없는 도구 실행 전 사람 승인 — 서버를 못 고칠 때의 안전장치)
   (7.guardrails:    코드가 판정 — 프롬프트 인젝션·rm -rf·PII·악성 MCP 서버(tool poisoning))
   (옛 문법 비교: 4.langchain/0.legacy(deprecated))
        ▼
[6단계] 실제 클라이언트에 붙이기 — 코드 없이 '설정'                  난이도 ★★
   3.anthropic/1.claude_desktop  Claude Desktop 에 내 서버 등록
   5.vscode/1.dev_helpers        Copilot/Cline/Continue/Claude Code 에 등록
   5.vscode/2.sql_helpers        내 DB 를 MCP 로 → 자연어로 SQL 질의(인증·보안 포함)
        ▼
[7단계] 실전 응용 프로젝트                                           난이도 ★★★
   10.projects/1.local(filesystem) → 2.remote(1.intro → 2.oauth 인증) → 3.codebase_qa (RAG 를 MCP 로 노출)
   → 4.mini_context7 → 5.chatbot_web → 6.multi_mcp_concierge → 7.multi_vendor_capstone
   (7.multi_vendor_capstone: 서버 하나에 OpenAI·Anthropic·LangChain 클라이언트가 동시에 붙는다 —
    "서버 한 번 만들면 어디서든 재사용"이라는 MCP 의 핵심 가치를 마지막에 직접 확인)
```

> **빠른 길**: 코드보다 결과를 먼저 보고 싶으면 1단계 → 5단계(Claude Desktop/VSCode 설정) 로 건너뛰어도 된다.
> 같은 서버를 어디에 붙이든 동작하는 게 MCP 의 핵심이기 때문.

## 빠른 시작

```bash
pip install mcp
cd 5.mcp/1.basic/1.intro && python 4.hello_client.py    # 첫 왕복 (LLM 불필요)
```
- **폴더별 상세·관전 포인트는 각 폴더 README** 참고. 특히 [`1.basic/README`](1.basic/) 에 **tool / resource / prompt** 개념 정리.
- 브라우저 클릭 테스트: `pip install "mcp[cli]"` → `mcp dev 1.basic/2.protocol_deep/5.server_tools_resource.py` (Node 18+ Inspector).

## 환경 설정

**가상환경은 레포 최상위에 하나만** 만들어 쓴다(하위 폴더별 venv ✗). `.venv/` 는 이미 gitignore.

```bash
# 레포 최상위(tutorial-genai/)에서 1번만
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell/CMD)
# source .venv/bin/activate       # macOS / Linux

pip install -r 5.mcp/requirements.txt   # mcp·uvicorn·openai·langchain 등 일괄

# 공식 MCP 서버(filesystem 등) 실행용 — pip 아님, 별도
node --version    # Node.js 18+ (npx)
```
- 개별 폴더만 빠르게 볼 땐 최소로 `pip install mcp` 만 해도 `1.basic` 은 동작한다.
- `.env` 에 `OPENAI_API_KEY`(2.openai·4.langchain), `ANTHROPIC_API_KEY`(3.anthropic) 가 필요할 수 있다.
  원격 인증 예제는 [`10.projects/2.remote/2.oauth/.env.example`](10.projects/2.remote/2.oauth/.env.example) 를 `.env` 로 복사해 쓴다.

## 더 보기
- **[`claude_code_mcp_guide.md`](claude_code_mcp_guide.md)** — Claude Code 에서 MCP 다루기(운영 가이드): 서버 출처(커넥터/project/local)·상태·인증(login/reconnect)·`claude mcp` 명령·**MCP 등록 vs 직접 설치(Bash)**
- 공식 문서: <https://modelcontextprotocol.io/>
- 공식 서버 모음: <https://github.com/modelcontextprotocol/servers>
- 파이썬 SDK: <https://github.com/modelcontextprotocol/python-sdk>

---
> **둘러보기**: [`5.vscode/`](5.vscode/) — VSCode Copilot Agent Mode 연동 워크스루 ·
> [`10.projects/3.codebase_qa/`](10.projects/3.codebase_qa/) — RAG 를 MCP 서버로 노출(GPT·Claude·LangChain·VSCode 재사용).
