# 에이전트 (Agents)

LLM 이 **도구를 자율적으로 사용**하여 작업을 수행하는 에이전트 패턴.
질문 → "어떤 도구 쓸까?" 판단 → 도구 실행 → 결과 보고 다음 결정 ... 반복.

## 폴더 구조

```
8.agents/
├── 0.agent_cap.py             ← 도구 목록 조회 유틸 (전체 입문)
│
├── 0.legacy(initialize_agent)/← deprecated initialize_agent 기반 (참고 보관용)
│   ├── 1.wikipedia/
│   ├── 2.arxiv/
│   ├── 3.custom_tools/
│   ├── 4.human_in_loop/
│   ├── 5.routing/
│   ├── 6.googlesearch/
│   └── 7.complex/
│
├── 1.basics/                  ← 현행 표준 입문 (bind_tools / 병렬 호출)
├── 2.builtin_tools/           ← 빌트인 도구 가져다 쓰기 (Wikipedia / arXiv / 웹검색)
├── 3.custom_tools/            ← @tool 데코레이터로 직접 만들기, Pydantic args
├── 4.langgraph_react/         ← LangGraph create_react_agent (현행 권장)
├── 5.routing_advanced/        ← 다중 도구 라우팅 + 복합 시나리오
├── 6.webscan_app/             ← 풀스택 (was 10.webscan_app)
└── README.md
```

> **방침**
> - 메인 폴더 (1~4) 는 **현행 API**: `bind_tools()`, `@tool`, `langgraph.prebuilt.create_react_agent`
> - `0.legacy(initialize_agent)/` 에는 **deprecated `initialize_agent` + `AgentType`** 기반 ~30개 파일 격리
> - 새 프로젝트는 1~4 만 따라가세요. legacy 는 "옛 코드 마이그레이션할 때 참고용"

## 학습 흐름

```
1.basics              ─ bind_tools, parallel tool calls 등 핵심 메커니즘
  1.1 llmmath_react
  1.2 bind_tools
  1.3 parallel_tool_calls
        ↓
2.builtin_tools       ─ 만들지 말고 가져다 쓰기 (Wikipedia/arXiv/Web Search)
  2.1 wikipedia
  2.2 arxiv
  2.3 web_search
        ↓
3.custom_tools        ─ 내가 직접 도구 정의 (@tool, Pydantic args)
  3.1 at_tool_basic
  3.2 pydantic_args
        ↓
4.langgraph_react     ─ create_react_agent 으로 자동 루프 + 메모리/HITL
  4.1 basic
  4.2 with_memory
  4.3 interrupt
        ↓
5.routing_advanced    ─ 다중 도구 라우팅, 복합 시나리오
  5.1 routing
  5.2 complex_agent
        ↓
6.webscan_app         ─ 실전 풀스택 (위 모든 도구 종합 응용)
```

## API 분류표

| API | 분류 | 권장도 | 위치 |
|-----|------|-------|------|
| `initialize_agent` + `AgentType.*` | ❌ Deprecated (v0.2+) | 신규 X | `0.legacy/` 만 |
| `AgentExecutor + create_tool_calling_agent` | △ 과도기 | 마이그레이션 단계만 | (없음) |
| `bind_tools()` + 수동 디스패치 | ✅ 저수준 표준 | 1-shot / 내부 이해 | `1.basics/1.2` |
| **`langgraph.prebuilt.create_react_agent`** | ✅ **현행 표준** | **신규 권장** | `4.langgraph_react/` |

## 폴더별 상세

### `1.basics/` — 현행 표준 입문
| 파일 | 설명 |
|------|------|
| `1.1_llmmath_react.py` | `create_react_agent` + LLMMath (가장 기본) |
| `1.2_bind_tools.py` | **NEW** — `llm.bind_tools()` 로 raw 도구 호출 보기 (수동 디스패치) |
| `1.3_parallel_tool_calls.py` | **NEW** — 한 응답에 여러 도구 동시 호출 (gpt-4o 기본 지원) |

### `2.builtin_tools/` — 빌트인 도구 가져다 쓰기
| 파일 | 설명 |
|------|------|
| `2.1_wikipedia.py` | Wikipedia 한/영 동시 사용, system prompt 로 한국어 답변 강제 |
| `2.2_arxiv.py` | arXiv 논문 검색 + 한국어 요약 |
| `2.3_web_search.py` | Tavily (권장) / Serper / Google CSE 비교 |

### `3.custom_tools/` — 도구 직접 정의
| 파일 | 설명 |
|------|------|
| `3.1_at_tool_basic.py` | **NEW** — `@tool` 데코레이터로 함수 → 도구화. docstring/타입힌트가 LLM 명세 |
| `3.2_pydantic_args.py` | **NEW** — `args_schema=PydanticModel` 로 인자 강하게 명세 (Field description, Literal enum, 검증 등) |

### `4.langgraph_react/` — 자동 루프 에이전트 (현행 권장)
| 파일 | 설명 |
|------|------|
| `4.1_basic.py` | **NEW** — `create_react_agent` 기본. 도구 호출 자동 루프 |
| `4.2_with_memory.py` | **NEW** — `MemorySaver` 로 thread_id 별 멀티턴 |
| `4.3_interrupt.py` | **NEW** — `interrupt_before=["tools"]` 로 도구 호출 전 사용자 승인 (HITL) |

### `5.routing_advanced/` — 다중 도구 + 복합 시나리오
| 파일 | 설명 |
|------|------|
| `5.1_routing.py` | 도구 여러 개 등록 → LLM 이 알아서 선택. legacy `9.smartagent_router*` 대체 |
| `5.2_complex_agent.py` | 여행 계획 에이전트 — 날씨/계산/위키 + 메모리 + 멀티턴 종합 |

### `6.webscan_app/` — 풀스택 (실전 응용)
| 파일 | 설명 |
|------|------|
| `scanapp.py` | 초기 버전 |
| `scanapp2_langgraph.py` | LangGraph 버전 (현행) |

### `0.legacy(initialize_agent)/` — Deprecated 격리

| 서브폴더 | 내용 | 옛 번호 |
|---------|------|--------|
| `1.wikipedia/` | Wikipedia 검색 에이전트 (한/영) | was 2.x |
| `2.arxiv/` | arXiv 논문 검색 + LCEL 체이닝 | was 3.x |
| `3.custom_tools/` | `@tool` 옛 사용법, Serper 등 | was 4.x |
| `4.human_in_loop/` | Human 도구 (옛 방식 — 지금은 LangGraph interrupt 권장) | was 5.x |
| `5.routing/` | 다중 도구 라우팅 / smartagent | was 6.x, 9.x |
| `6.googlesearch/` | Google 검색 + 번역 체이닝 | was 7.x |
| `7.complex/` | 복합 에이전트 | was 8.x |

> ⚠️ 이 폴더 안의 코드는 `initialize_agent` + `AgentType.ZERO_SHOT_REACT_DESCRIPTION` 기반으로 LangChain v0.2+ deprecated. **참고 용도로만** 보세요.

## 핵심 API 비교

### Legacy (사용 금지)
```python
from langchain.agents import initialize_agent, AgentType
agent = initialize_agent(tools, llm, AgentType.ZERO_SHOT_REACT_DESCRIPTION)
result = agent.run("질문")
```

### 현행 (권장)
```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("user", "질문")]})
```

## 관련 폴더

- [`../3.structured_output/`](../3.structured_output/) — 에이전트 응답을 Pydantic 으로 받기
- [`../4.chaining/`](../4.chaining/) — `bind_tools()` 가 LCEL Runnable
- [`../6.memory/`](../6.memory/) — `MemorySaver` 가 에이전트 메모리의 핵심
- [`../7.RAG/5.agentic/`](../7.RAG/5.agentic/) — RAG 에 에이전트 패턴 적용
- [`../9.langgraph/`](../9.langgraph/) — LangGraph 본격 학습

## 실행

```bash
pip install langchain langchain-openai langchain-community langgraph python-dotenv

# 현행 표준
python "1.basics/1.1_llmmath_react.py"
python "4.langgraph_react/4.1_basic.py"

# Legacy 참고용 (실행 시 deprecation warning)
python "0.legacy(initialize_agent)/1.wikipedia/2.1_wikipedia1.py"
```
