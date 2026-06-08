# 에이전트 (Agents)

LLM 이 **도구를 자율적으로 사용**하여 작업을 수행하는 에이전트 패턴.
질문 → "어떤 도구 쓸까?" 판단 → 도구 실행 → 결과 보고 다음 결정 ... 반복.

## 폴더 구조

```
8.agents/
├── 0.legacy(initialize_agent)/   ← 옛 initialize_agent 기반 (블로그 참조용)
│
├── 1.builtin_tools/              ← 가져다 쓰기 (최소 → 빌드업). 가장 단순한 첫 에이전트
├── 2.custom_tools/               ← @tool 로 내 도구 정의
├── 3.applied_agents/             ← 빌트인 + 커스텀 혼합 응용 (+ 에이전틱 RAG)
├── 4.internals/                  ← 저수준/운영 (bind_tools / parallel / safety / 에러 / 트레이싱 / 토큰)
├── 5.langgraph_memory/           ← 메모리 (멀티턴 / 장기기억 / trim / sqlite 영속)
├── 6.hitl_streaming/             ← 사람 승인 / 스트리밍 UX
├── 7.routing/                    ← 다중 도구 라우팅 + 복합 시나리오
├── 8.mcp/                        ← (포인터) MCP 는 최상위 /8.mcp 로 이전
├── 9.agentic_patterns/           ← Anthropic 5대 워크플로우 패턴 (체이닝/라우팅/병렬/오케스트레이터/평가자)
├── 10.multi_agent/               ← 멀티 에이전트 (에이전트를 도구로 / 슈퍼바이저)
├── 11.evaluation/                ← 에이전트 평가 (도구 선택 정확도 등 자동 검증)
├── 12.middleware/                ← create_agent 미들웨어 (요약 / PII 가드레일 / 커스텀 훅)
│
├── 20.mini_apps/                 ← 실전 미니 앱 모음 (webscan · 금융조회 · 가상트레이딩+HITL · 카드뉴스)
│                                    ← 학습 토픽이 아니라 '통합 앱' POC. 필요한 시점에 조립.
└── README.md
```

> **방침**
> - 메인 폴더 (1~12) 는 모두 **현행 API**: `create_agent` / `@tool` / `bind_tools` / `middleware`
>   (LangChain 1.0+ — 옛 `langgraph.prebuilt.create_react_agent` 는 `langchain.agents.create_agent` 로 이동·대체)
> - `0.legacy(initialize_agent)/` 에 옛 `initialize_agent + AgentType.*` 기반 32개 파일 격리
> - 각 파일 상단 docstring 에 (1) 모듈 한 줄 정의 + (2) 이 예제의 목적 명시
> - 라이브 코딩 가능한 길이 (~50~120줄)

## 학습 흐름 — "가져다 쓰기 → 만들기 → 응용 → 고급"

```
1.builtin_tools     ─ create_agent + 이미 만들어둔 도구 (최소 한 줄 → 한/영·안전장치 빌드업)
       ↓
2.custom_tools      ─ @tool 로 내 도구 정의 (+ Pydantic args, structured output)
       ↓
3.applied_agents    ─ 빌트인 + 커스텀 도구를 한 에이전트에 혼합 (멀티툴 라우팅)
       ↓
4.internals         ─ bind_tools / parallel_tool_calls / safety (내부 동작 / 운영)
       ↓
5.langgraph_memory  ─ MemorySaver + thread_id 로 멀티턴
       ↓
6.hitl_streaming    ─ interrupt (HITL) + stream (UX)
       ↓
7.routing           ─ 다중 도구 + 복합 시나리오 (여행 플래너 등)
       ↓
8.mcp               ─ MCP 표준 프로토콜로 외부 서버 도구 사용
       ↓
9.agentic_patterns  ─ Anthropic 5대 워크플로우 패턴 (체이닝/라우팅/병렬/오케스트레이터/평가자)
       ↓
10.multi_agent      ─ 멀티 에이전트 (에이전트를 도구로 / 슈퍼바이저 / 병렬 분석)
       ↓
11.evaluation       ─ 에이전트 평가 (도구 선택 정확도 자동 검증)
       ↓
12.middleware       ─ create_agent 미들웨어 (요약 / PII 가드레일 / 커스텀 훅)
       ┊
20.mini_apps        ─ (학습 흐름과 별개) 위 패턴들을 '통합 앱' 으로 조립한 POC
                       webscan / 금융조회 / 가상트레이딩 + 이메일 HITL / 카드뉴스
```

## API 분류표

| API | 분류 | 권장도 | 위치 |
|-----|------|-------|------|
| `initialize_agent` + `AgentType.*` | ❌ Deprecated (v0.2+) | 신규 ✗ | `0.legacy/` 만 |
| `bind_tools()` + 수동 디스패치 | ✅ 저수준 표준 | 1-shot / 내부 이해 | `4.internals/4.1` |
| `langchain.agents.create_agent` | ✅ **현행 표준** (LangChain 1.x) | **신규 권장** | 1~3, 5~7, 10 |
| `langgraph.prebuilt.create_react_agent` | ⚠️ 구 위치 (deprecated 이동) | → `create_agent` 사용 | `2.custom_tools/2.1` 주석의 마이그레이션 노트 |
| `MultiServerMCPClient` (MCP) | ✨ 표준 프로토콜 | 외부 도구 재사용 | `8.mcp/` |

> **마이그레이션:** `from langgraph.prebuilt import create_react_agent` → `from langchain.agents import create_agent`,
> 인자 `prompt=` → `system_prompt=`. 사용법(`invoke`/`stream`/`checkpointer`/`interrupt_before`)은 동일.
> 그래프 LLM 노드 이름만 `agent` → `model` 로 바뀜(스트리밍 노드명 볼 때만 영향). 변경 상세는 `2.custom_tools/2.1_first_agent.py` 주석 참고.

## 핵심 함수·메서드 한눈에

에이전트를 다루며 **배우게 될 주요 함수/메서드**입니다. (상세 실습은 각 폴더에서)
모든 에이전트는 LangGraph `CompiledStateGraph` 라서, 아래 실행/상태 메서드는 공통으로 쓸 수 있습니다.

### 생성
| 함수 | 하는 일 | 배우는 곳 |
|---|---|---|
| `create_agent(model, tools, ...)` | LLM+도구를 묶어 에이전트(그래프) 생성. 핵심 인자: `system_prompt=` / `checkpointer=` / `interrupt_before=` / `response_format=` | 1.builtin_tools |
| `@tool` | 파이썬 함수 → 에이전트 도구 (docstring·타입힌트가 곧 명세) | 2.custom_tools |
| `llm.bind_tools([...])` | (저수준) LLM 에 도구만 바인딩 — ReAct 루프는 직접 | 4.1 |

### 실행
| 메서드 | 하는 일 | 배우는 곳 |
|---|---|---|
| `agent.invoke({"messages":[...]}, config=)` | 한 번 실행 → 최종 상태(dict) 반환 | 1.builtin_tools |
| `agent.ainvoke(...)` | 비동기 실행 (MCP 등 async 도구) | 8.mcp |
| `agent.stream(..., stream_mode=...)` | 스트리밍 — `"updates"`(노드별) / `"messages"`(토큰) / `"values"`(전체 스냅샷) | 6.2 |

### 상태·메모리 (checkpointer 필요)
| 메서드 | 하는 일 | 배우는 곳 |
|---|---|---|
| `agent.get_state(config)` | 그 thread 의 **현재 상태**(messages 등) 조회 | 5.3 |
| `agent.get_state_history(config)` | **과거 스냅샷**(체크포인트) 목록 — 디버깅/되감기 | 5.3 |
| `agent.update_state(config, {...})` | 상태 직접 **수정** — HITL 에서 도구 인자 교정·거부 | 6.1, 6.3 |

### 자주 쓰는 구성요소
| 이름 | 하는 일 | 배우는 곳 |
|---|---|---|
| `MemorySaver()` | in-memory 체크포인터(메모리). 영속화는 `SqliteSaver`/`PostgresSaver` 로 교체 | 5.langgraph_memory |
| `InMemoryStore()` | thread 를 넘어 유지되는 **장기 메모리**. `put`/`search`/`get`. 영속화는 `PostgresStore` | 5.4 |
| `config={"configurable":{"thread_id":...}}` | 세션 구분 키 (+ `recursion_limit` 등 실행 옵션) | 5.langgraph_memory, 4.3 |
| `interrupt_before=["tools"]` | 도구 실행 **직전 정지** (사람 승인/수정) | 6.1, 6.2, 6.4, 6.5 |
| `response_format=Pydantic` | 최종 답을 구조화 → `result["structured_response"]` | 2.6 |
| `MultiServerMCPClient` | MCP 서버 도구 → LangChain 도구로 자동 변환 | 8.mcp |

## 폴더별 파일 상세

### `1.builtin_tools/` — 가져다 쓰기 (도구별 최소 → 빌드업)
> `1.0` 카탈로그(LLM 호출 없음), `1.1` llm-math(가장 기초). 이후 **도구 유형별로 묶고** 각 그룹 안에서 최소 → 완전 순:
> wikipedia(`1.2~1.4`) · web_search(`1.5~1.6`) · arxiv(`1.7~1.8`).

| 파일 | 설명 |
|---|---|
| `1.0_list_all_tools.py` | `load_tools` 로 가져올 수 있는 빌트인 카탈로그 (시작점, 에이전트 X) |
| `1.1_llm_math.py` | `load_tools(["llm-math"]) + create_agent` — 가장 기초 도구(Calculator), 자연어 수식 계산 |
| `1.2_wikipedia_minimal.py` | `load_tools(["wikipedia"]) + create_agent` 한 줄 — 도구 안 만들고 첫 에이전트 |
| `1.3_wikipedia.py` | (빌드업) 한국어 + 영어 위키 동시 + system_prompt + recursion_limit |
| `1.4_wikipedia_think.py` | 동일 에이전트를 **reasoning 모델** (gpt-5-mini / Claude thinking) 로 — thinking 함께 출력 |
| `1.5_web_search_minimal.py` | Tavily 검색 도구 1개 (최소) |
| `1.6_web_search.py` | (빌드업) Tavily (권장) / Serper / Google CSE 비교 |
| `1.7_arxiv_minimal.py` | 같은 골격, 도구만 arxiv 로 교체 (최소) |
| `1.8_arxiv.py` | (빌드업) 학술 논문 검색 + 한국어 요약/번역 |
| `1.9_human.py` | `load_tools(["human"])` — 모르는 정보를 사용자에게 직접 되묻기 (가장 단순한 HITL) |

### `2.custom_tools/` — 내 도구 정의
| 파일 | 설명 |
|---|---|
| `2.1_first_agent.py` | 도구 1개 (계산기) 를 직접 만들어 `create_agent` 에 — **현행** (옛 `create_react_agent` → `create_agent` 마이그레이션 주석 포함) |
| `2.2_at_tool_basic.py` | `@tool` 데코레이터 — 함수 → 도구. docstring + 타입힌트가 LLM 명세 |
| `2.3_at_tool_basic2_exec.py` | 2.2 확장 — 시스템 프롬프트 + 빈 `tool_calls` 처리로 적합한 도구 없으면 "없다"고 답하게 |
| `2.4_pydantic_args.py` | `args_schema=PydanticModel` — Field description / Literal enum / 검증 |
| `2.5_pydantic_args2_exec.py` | 2.4 확장 — 도구 vs 직접답변 LLM 이 선택 + 고른 도구를 `@tool.invoke` 로 **실제 실행**까지 |
| `2.6_structured_output.py` | `response_format=Pydantic` — 에이전트 최종 답변을 구조화된 dict 로 |
| `2.7_sql_tool.py` | SQLite 스키마 → 자연어 질문 → SQL 생성·**실제 실행**·결과 (text-to-SQL, create_agent) |

### `3.applied_agents/` — 응용 (빌트인 + 커스텀 혼합)
| 파일 | 설명 |
|---|---|
| `3.1_multi_tools.py` | 도구 3개 → LLM 이 알아서 라우팅, 도구 없는 질문은 직접 답 |
| `3.2_builtin_plus_custom.py` | 위키(빌트인) + 계산기(커스텀) 를 한 리스트에 — "사실 조회 → 계산" 연쇄 |
| `3.3_retriever_tool.py` | **에이전틱 RAG** — 벡터스토어 검색을 `@tool` 로 단 에이전트(필요할 때만 검색). 고정 RAG 파이프라인과 대비 |

### `4.internals/` — 저수준 / 운영
| 파일 | 설명 |
|---|---|
| `4.1_bind_tools.py` | create_agent 내부 ReAct 루프를 손으로 짜보기 |
| `4.2_parallel_tool_calls.py` | gpt-4o 의 한 응답에 여러 도구 동시 호출 (LLM 호출 횟수 ↓) |
| `4.3_safety.py` | `recursion_limit` / try-except / 입력 검증 — 운영 필수 |
| `4.4_tool_errors.py` | 도구가 예외를 던질 때 — 기본은 전파(중단) / 도구 내 try-except / `ToolRetryMiddleware` 자동 재시도 |
| `4.5_langsmith_tracing.py` | **관측성** — 환경변수만으로 LangSmith 트레이싱 ON (모델/도구/토큰/지연 기록) |
| `4.6_token_usage.py` | **토큰/비용 추적** — `usage_metadata` 로 호출별 토큰 합산·대략 비용 |

### `5.langgraph_memory/` — 멀티턴
| 파일 | 설명 |
|---|---|
| `5.1_with_memory.py` | `MemorySaver` + `thread_id` 별 격리. 같은 thread 안 맥락 유지 |
| `5.2_multi_session.py` | 같은 에이전트, `thread_id` 다르면 기억 안 섞임 (멀티유저 격리) |
| `5.3_inspect_state.py` | `get_state` / `get_state_history` 로 저장된 메모리 직접 들여다보기 |
| `5.4_long_term_store.py` | **장기 메모리** — `Store` 로 thread(세션) 를 넘어 유지되는 기억 (checkpointer=단기와 대비) |
| `5.5_trim_messages.py` | **컨텍스트 관리** — `trim_messages` 로 오래된 메시지 잘라내기(개수/토큰 기준). 요약(12.1)과 대비 |
| `5.6_sqlite_checkpointer.py` | **영속 체크포인터** — `SqliteSaver` 로 대화를 파일에 저장(재시작해도 복구). `MemorySaver` 한 줄 교체 |

### `6.hitl_streaming/` — 사용자 제어 / UX
| 파일 | 설명 |
|---|---|
| `6.1_ask_once.py` | 가장 단순한 HITL — 도구 실행 전 y/n **한 번** 묻고 진행 (y 실행·결과 / n 중단) |
| `6.2_interrupt.py` | `interrupt_before=["tools"]` — 도구를 여러 번 부를 때 호출마다 반복 승인 (+ 특정 도구 전에만 멈추는 법) |
| `6.3_streaming.py` | `agent.stream()` — 노드 단위 / 토큰 단위 두 모드 비교 |
| `6.4_edit_and_resume.py` | 정지 후 도구 인자를 코드로 **수정**하고 재개 (`update_state` 로 tool_calls 교정) |
| `6.5_ask_or_edit.py` | 진행/취소/**수정** 메뉴 — 사람이 실행 중 금액을 직접 입력해 송금, 남은 잔고 출력 |

### `7.routing/` — 다중 도구
| 파일 | 설명 |
|---|---|
| `7.1_basic_routing.py` | 도구 여러 개 등록만 하면 LLM 이 알아서 선택. 별도 라우터 불필요 |
| `7.2_complex_agent.py` | 여행 플래너 — 날씨/계산/위키 + 메모리 + 멀티턴 종합 |

### `8.mcp/` — Model Context Protocol → 최상위 [`/8.mcp`](../../8.mcp/) 로 이전됨
> MCP 는 provider/framework 중립 주제라 분량이 커서 **레포 최상위 [`8.mcp/`](../../8.mcp/)** 로 승격했습니다.
> 공통(서버 만들기·프로토콜) / openai / anthropic / langchain / vscode / projects 로 분류되어 있습니다.
>
> LangChain 에이전트에서 MCP 를 쓰는 부분만 보려면 → [`/8.mcp/4.langchain/`](../../8.mcp/4.langchain/)
> (`0.quickstart` = adapters 빠른 시작, `1.langchain_agent` · `2.langchain_bridge` · `3.tools_safety` = 심화)

### `9.agentic_patterns/` — Anthropic 워크플로우 패턴
> [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) 의 5대 패턴. 상세는 `9.agentic_patterns/README.md`.

| 파일 | 패턴 | 주요 기술 |
|---|---|---|
| `9.1_prompt_chaining.py` | Prompt Chaining (순차 파이프라인) | LCEL 체인 |
| `9.2_routing.py` | Routing (분류 → 전문 체인 분기) | RunnableLambda |
| `9.3_parallelization_eg1.py` | Parallelization 팬아웃/팬인 (다관점) | RunnableParallel |
| `9.3_parallelization_eg2.py` | Parallelization LLM-as-judge 단일점수 (후보→선택) | batch / 구조화 출력 |
| `9.3_parallelization_eg3.py` | Parallelization LLM-as-judge 쌍대비교 토너먼트 | batch / 구조화 출력 |
| `9.4_orchestrator_worker.py` | Orchestrator-Worker (동적 작업 분해) | LangGraph StateGraph |
| `9.5_evaluator_optimizer.py` | Evaluator-Optimizer (생성→평가→개선 루프) | LangGraph 순환 그래프 |

### `10.multi_agent/` — 멀티 에이전트
> 전문 에이전트로 나누고 서로 위임. `10.1` 은 `create_agent`(내장 그래프 자동 구성) 재사용, `10.2`/`10.3` 은 `StateGraph` 를 직접 구성. 상세는 `10.multi_agent/README.md`.

| 파일 | 패턴 | 그래프 | 설명 |
|---|---|---|---|
| `10.1_agent_as_tool.py` | Agent-as-Tool | 내장(자동) | 전문 에이전트를 `@tool` 로 포장해 호출 (가장 단순) |
| `10.2_supervisor.py` | Supervisor | **StateGraph** | `START`/`END` + 조건부 엣지로 '관리자 ↔ worker' 루프 직접 구성 |
| `10.3_finance_analyst.py` | 병렬 분석가 | **StateGraph** | 주가(yfinance)·뉴스 worker 를 **병렬**(fan-out)로 돌려 합류(fan-in) 후 종합 |

> **`create_agent` 가 이미 LangGraph 그래프**(`START→model→tools→END`)라, **단일 에이전트면 START/END 를 직접 안 짜도 됩니다**(`10.1`).
> 병렬·조건분기·루프 등 **고정 ReAct 모양으로 안 되는 흐름**일 때만 `StateGraph` 로 직접 구성(`10.2`/`10.3`).

### `11.evaluation/` — 에이전트 평가
> 비결정적 에이전트의 회귀를 잡으려면 자동 평가가 필요. 상세는 `11.evaluation/README.md`.

| 파일 | 설명 |
|---|---|
| `11.1_tool_call_eval.py` | **도구 선택 정확도** 자동 채점 — 불러야 할 때 부르고/아닐 때 안 부르는가 (외부 의존성 없음) |

### `12.middleware/` — create_agent 미들웨어
> `create_agent(middleware=[...])` 로 끼우는 플러그인 — langchain 1.x 의 표준 확장 방식. 상세는 `12.middleware/README.md`.

| 파일 | 미들웨어 | 설명 |
|---|---|---|
| `12.1_summarization.py` | `SummarizationMiddleware` | 긴 대화를 요약으로 압축 (컨텍스트 관리, trim=5.5 와 대비) |
| `12.2_pii_guardrail.py` | `PIIMiddleware` | 이메일·카드번호 등 민감정보 마스킹/차단 (가드레일) |
| `12.3_custom_middleware.py` | `AgentMiddleware` 상속 | 직접 작성 — `before_model`/`after_model` 훅으로 로깅·집계 |

> 그 외 내장: `ToolRetryMiddleware`(4.4) · `HumanInTheLoopMiddleware`(6 과 비교) · `ModelCallLimitMiddleware` 등

### `20.mini_apps/` — 실전 미니 앱 모음
> 학습 토픽이 아니라, 앞 패턴들을 **돌아가는 통합 앱**으로 조립한 POC. 상세는 `20.mini_apps/README.md`.

| 앱 | 설명 | 핵심 패턴 |
|---|---|---|
| `1.webscan_cli/` | 시스템 점검 어시스턴트 (**CLI**) | 도구 모듈화 + 메모리 |
| `2.webscan_app_web/` | 같은 점검 에이전트의 **웹(Flask)** 버전 (`@tool` 6종 + MemorySaver) | 도구 모듈화 + 메모리 |
| `3.finance_bot/` | 뉴스/기업정보/환율/주가 조회 봇 (CLI) | 멀티툴 라우팅 |
| `4.trading_bot/` | 조건 충족 시 **이메일 승인(HITL)** 후 가상 거래 ⚠️샌드박스 | cron 잡 + out-of-band HITL |
| `5.trading_bot_web/` | **챗봇**으로 잔고·시세 묻고 예약/매매 → **알림/승인** 후 가상 거래 ⚠️샌드박스 | 대화형 에이전트 + 웹 HITL |
| `6.cardview_news/` | **주제 → 뉴스 → 요약 → 카드뉴스 이미지** 생성 (`app2_lcel.py` = LCEL 버전) | 도구 + 이미지 생성(멀티모달) · LCEL |

> `4.trading_bot` 은 `6.hitl_streaming` 의 인프로세스 `interrupt_before` 와 대비되는
> **비동기(out-of-band) HITL** — 에이전트가 주기적으로 돌다 위험 액션 직전 이메일로 승인 요청.

### `0.legacy(initialize_agent)/` — Deprecated 격리

옛 `initialize_agent + AgentType.ZERO_SHOT_REACT_DESCRIPTION` 기반 32개 파일.
**새 코드에는 쓰지 마세요.** 옛 블로그 코드 마이그레이션 시 참고용.

| 서브폴더 | 내용 |
|---|---|
| `1.wikipedia/` | Wikipedia 검색 (한/영) |
| `2.arxiv/` | arXiv 검색 + LCEL 체이닝 |
| `3.custom_tools/` | `@tool` 옛 사용법, Serper |
| `4.human_in_loop/` | Human 도구 — 지금은 LangGraph interrupt 권장 |
| `5.routing/` | 직접 라우터 + smartagent — 지금은 LLM tool calling 으로 충분 |
| `6.googlesearch/` | Google CSE + 번역 체이닝 |
| `7.complex/` | 복합 에이전트 |

## 핵심 API 비교

### Legacy (사용 금지)
```python
from langchain.agents import initialize_agent, AgentType
agent = initialize_agent(tools, llm, AgentType.ZERO_SHOT_REACT_DESCRIPTION)
result = agent.run("질문")
```

### 현행 (권장, LangChain 1.x)
```python
from langchain.agents import create_agent
agent = create_agent(llm, tools)                       # system_prompt= 로 시스템 프롬프트 지정
result = agent.invoke({"messages": [("user", "질문")]})
```

## 자주 묻는 질문 (FAQ)

**Q. `@tool` 의 docstring 이 정말로 LLM 에 보내지나?**
→ 네. docstring + 타입 힌트가 LLM 의 tool calling JSON Schema 가 됩니다.
   `2.custom_tools/2.2` 에서 직접 출력해서 확인할 수 있어요.

**Q. 도구 여러 개 등록하면 모델이 매번 다 보내나? 토큰 부담은?**
→ 도구 정의가 매 요청의 시스템 프롬프트 같은 자리에 포함됩니다. 도구가 너무 많으면
   라우팅 정확도 ↓ + 토큰 ↑. 보통 5~10 개 이하로 유지하고, 필요하면 도메인별로
   에이전트 분리.

**Q. 에이전트가 무한 루프에 빠지면?**
→ `4.internals/4.3_safety.py` 참고. `recursion_limit` 으로 LangGraph 노드 호출
   상한 강제. 운영에서는 보통 10~25 정도.

**Q. MCP 와 @tool 의 차이는?**
→ @tool 은 LangChain 안에서만 도구로 인식. MCP 는 표준 프로토콜이라 같은 서버를
   Claude Desktop / Cursor / LangChain 등 어디서든 재사용 가능. `8.mcp/` 참고.

## 관련 폴더

- [`../3.structured_output/`](../3.structured_output/) — 에이전트 응답 구조화 (`response_format`)
- [`../4.chaining/`](../4.chaining/) — `bind_tools()` 가 LCEL Runnable
- [`../6.memory/`](../6.memory/) — `MemorySaver` 가 에이전트 메모리의 핵심
- [`../7.RAG/6.agentic/`](../7.RAG/6.agentic/) — RAG 에 에이전트 패턴 적용
- [`../9.langgraph/`](../9.langgraph/) — LangGraph 본격 학습

## 설치 & 실행

```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv

# 1.builtin_tools
pip install wikipedia arxiv langchain-tavily

# 8.mcp 는 최상위 /8.mcp 로 이전됨 — 설치/실행은 8.mcp/README.md 참고
pip install mcp langchain-mcp-adapters          # LangChain↔MCP 연동 (+ 공식 서버는 Node.js 18+)

# 10.multi_agent (10.3_finance_analyst 는 주가/뉴스 조회)
pip install yfinance requests

# 5.6 영속 체크포인터
pip install langgraph-checkpoint-sqlite

# 20.mini_apps
pip install flask psutil requests yfinance apscheduler bs4   # webscan / finance / trading / cardnews
```
> `3.3_retriever_tool`(임베딩)·`12.middleware`(미들웨어)·`4.5_langsmith_tracing`은 위 기본 패키지로 동작합니다.
> `4.5`의 트레이싱은 선택: `.env` 에 `LANGSMITH_TRACING=true` / `LANGSMITH_API_KEY=...` 설정 시에만 기록.

각 폴더에서 실행:
```bash
cd "2.langchain/8.agents/1.builtin_tools"
python 1.1_llm_math.py           # llm-math(Calculator) — 가장 기초 도구 에이전트

cd "../10.multi_agent" && python 10.1_agent_as_tool.py   # 에이전트를 도구로 위임 (내장 그래프)
python 10.2_supervisor.py                                # StateGraph 슈퍼바이저 (START/END 직접)
python 10.3_finance_analyst.py                           # StateGraph 병렬 분석 (주가+뉴스 종합)
cd "../11.evaluation" && python 11.1_tool_call_eval.py   # 도구 선택 정확도 평가
cd "../12.middleware" && python 12.1_summarization.py    # 미들웨어: 긴 대화 자동 요약
python 12.2_pii_guardrail.py                             # 미들웨어: PII 마스킹(가드레일)

cd "../20.mini_apps/1.webscan_cli"
python app.py                                 # 시스템 점검 (CLI)

cd "../2.webscan_app_web" && python app.py    # 같은 점검 에이전트 웹판 → http://localhost:5000
cd "../3.finance_bot" && python app.py        # 금융 조회 봇 (CLI)
cd "../4.trading_bot" && python app.py        # 가상 트레이딩 + 이메일 HITL → http://localhost:5001
cd "../5.trading_bot_web" && python app.py    # 챗봇 가상 트레이딩 → http://localhost:5003
```
