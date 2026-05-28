# 에이전트 (Agents)

LLM 이 **도구를 자율적으로 사용**하여 작업을 수행하는 에이전트 패턴.
질문 → "어떤 도구 쓸까?" 판단 → 도구 실행 → 결과 보고 다음 결정 ... 반복.

## 폴더 구조

```
8.agents/
├── 0.legacy(initialize_agent)/   ← 옛 initialize_agent 기반 (블로그 참조용)
│
├── 1.basics/                     ← 첫 에이전트 만들기 (가장 단순)
├── 2.custom_tools/               ← @tool 로 내 도구 정의
├── 3.builtin_tools/              ← 만들지 말고 가져다 쓰기 (Wikipedia / arXiv / 웹검색)
├── 4.memory/                     ← 멀티턴 대화 (MemorySaver + thread_id)
├── 5.hitl_streaming/             ← 사람 승인 / 스트리밍 UX
├── 6.routing/                    ← 다중 도구 라우팅 + 복합 시나리오
├── 7.internals/                  ← 저수준 메커니즘 (참고)
├── 8.mcp/                        ← MCP (Model Context Protocol) — 표준 도구 프로토콜
├── 9.webscan_app/                ← 실전 풀스택 (Flask + 에이전트)
└── README.md
```

> **방침**
> - 메인 폴더 (1~9) 는 모두 **현행 API**: `create_react_agent` / `@tool` / `bind_tools`
> - `0.legacy(initialize_agent)/` 에 옛 `initialize_agent + AgentType.*` 기반 32개 파일 격리
> - 각 파일 상단 docstring 에 (1) 모듈 한 줄 정의 + (2) 이 예제의 목적 명시
> - 라이브 코딩 가능한 길이 (~50~120줄)

## 학습 흐름 — "사용 → 만들기 → 고급 → 응용"

```
1.basics            ─ create_react_agent 한 줄로 에이전트 만들기
       ↓
2.custom_tools      ─ @tool 로 내 도구 정의 (+ Pydantic args, structured output)
       ↓
3.builtin_tools     ─ 이미 만들어둔 것 가져다 쓰기 (Wikipedia / arXiv / Tavily)
       ↓
4.memory            ─ MemorySaver + thread_id 로 멀티턴
       ↓
5.hitl_streaming    ─ interrupt (HITL) + stream (UX)
       ↓
6.routing           ─ 다중 도구 + 복합 시나리오 (여행 플래너 등)
       ↓
7.internals         ─ bind_tools / parallel_tool_calls / safety (저수준 / 운영)
       ↓
8.mcp               ─ MCP 표준 프로토콜로 외부 서버 도구 사용
       ↓
9.webscan_app       ─ 실전 풀스택 (Flask + create_react_agent + @tool 모듈화)
```

## API 분류표

| API | 분류 | 권장도 | 위치 |
|-----|------|-------|------|
| `initialize_agent` + `AgentType.*` | ❌ Deprecated (v0.2+) | 신규 ✗ | `0.legacy/` 만 |
| `bind_tools()` + 수동 디스패치 | ✅ 저수준 표준 | 1-shot / 내부 이해 | `7.internals/7.1` |
| `langgraph.prebuilt.create_react_agent` | ✅ **현행 표준** | **신규 권장** | 1~6, 9 |
| `MultiServerMCPClient` (MCP) | ✨ 표준 프로토콜 | 외부 도구 재사용 | `8.mcp/` |

## 폴더별 파일 상세

### `1.basics/` — 첫 에이전트
| 파일 | 설명 |
|---|---|
| `1.1_first_agent.py` | 도구 1개 (계산기) + create_react_agent 한 줄로 |
| `1.2_multi_tools.py` | 도구 3개 → LLM 이 알아서 라우팅, 도구 없는 질문은 직접 답 |

### `2.custom_tools/` — 내 도구 정의
| 파일 | 설명 |
|---|---|
| `2.1_at_tool_basic.py` | `@tool` 데코레이터 — 함수 → 도구. docstring + 타입힌트가 LLM 명세 |
| `2.2_pydantic_args.py` | `args_schema=PydanticModel` — Field description / Literal enum / 검증 |
| `2.3_structured_output.py` | `response_format=Pydantic` — 에이전트 최종 답변을 구조화된 dict 로 |

### `3.builtin_tools/` — 가져다 쓰기
| 파일 | 설명 |
|---|---|
| `3.0_list_all_tools.py` | `load_tools` 로 가져올 수 있는 빌트인 카탈로그 |
| `3.1_wikipedia.py` | 한국어 + 영어 위키 동시 사용 |
| `3.1_wikipedia_think.py` | 동일한 에이전트를 **reasoning 모델** (gpt-5-mini / Claude thinking) 로 — thinking 함께 출력 |
| `3.2_arxiv.py` | 학술 논문 검색 + 한국어 요약/번역 |
| `3.3_web_search.py` | Tavily (권장) / Serper / Google CSE 비교 |

### `4.memory/` — 멀티턴
| 파일 | 설명 |
|---|---|
| `4.1_with_memory.py` | `MemorySaver` + `thread_id` 별 격리. 같은 thread 안 맥락 유지 |

### `5.hitl_streaming/` — 사용자 제어 / UX
| 파일 | 설명 |
|---|---|
| `5.1_interrupt.py` | `interrupt_before=["tools"]` — 위험한 도구 호출 전 사람 승인 |
| `5.2_streaming.py` | `agent.stream()` — 노드 단위 / 토큰 단위 두 모드 비교 |

### `6.routing/` — 다중 도구
| 파일 | 설명 |
|---|---|
| `6.1_basic_routing.py` | 도구 여러 개 등록만 하면 LLM 이 알아서 선택. 별도 라우터 불필요 |
| `6.2_complex_agent.py` | 여행 플래너 — 날씨/계산/위키 + 메모리 + 멀티턴 종합 |

### `7.internals/` — 저수준 / 운영
| 파일 | 설명 |
|---|---|
| `7.1_bind_tools.py` | create_react_agent 내부 ReAct 루프를 손으로 짜보기 |
| `7.2_parallel_tool_calls.py` | gpt-4o 의 한 응답에 여러 도구 동시 호출 (LLM 호출 횟수 ↓) |
| `7.3_safety.py` | `recursion_limit` / try-except / 입력 검증 — 운영 필수 |

### `8.mcp/` — Model Context Protocol
| 파일 | 설명 |
|---|---|
| `8.1_mcp_intro.py` | MCP 가 뭐고 왜 표준이 되어가는지 (개념 정리) |
| `8.2_mcp_client.py` | `langchain-mcp-adapters` 로 filesystem MCP 서버 도구를 에이전트에 |

### `9.webscan_app/` — 실전 풀스택
| 파일 | 설명 |
|---|---|
| `tools.py` | `@tool` 로 정의된 시스템 점검 도구 6종 (포트/SSL/웹/리소스/프로세스/네트워크) |
| `app.py` | Flask + create_react_agent + MemorySaver. JSON API + 멀티턴 |
| `templates/index.html` | 자연어 입력 UI + 사용된 도구 표시 + 예시 버튼 |
| `static/style.css` | 최소 CSS (시맨틱 HTML 이라 없어도 읽힘) |

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

### 현행 (권장)
```python
from langgraph.prebuilt import create_react_agent
agent = create_react_agent(llm, tools)
result = agent.invoke({"messages": [("user", "질문")]})
```

## 자주 묻는 질문 (FAQ)

**Q. `@tool` 의 docstring 이 정말로 LLM 에 보내지나?**
→ 네. docstring + 타입 힌트가 LLM 의 tool calling JSON Schema 가 됩니다.
   `2.custom_tools/2.1` 에서 직접 출력해서 확인할 수 있어요.

**Q. 도구 여러 개 등록하면 모델이 매번 다 보내나? 토큰 부담은?**
→ 도구 정의가 매 요청의 시스템 프롬프트 같은 자리에 포함됩니다. 도구가 너무 많으면
   라우팅 정확도 ↓ + 토큰 ↑. 보통 5~10 개 이하로 유지하고, 필요하면 도메인별로
   에이전트 분리.

**Q. 에이전트가 무한 루프에 빠지면?**
→ `7.internals/7.3_safety.py` 참고. `recursion_limit` 으로 LangGraph 노드 호출
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

# 3.builtin_tools
pip install wikipedia arxiv langchain-tavily

# 8.mcp
pip install langchain-mcp-adapters
# + Node.js (MCP 서버 실행용)

# 9.webscan_app
pip install flask psutil requests
```

각 폴더에서 실행:
```bash
cd "2.langchain/8.agents/1.basics"
python 1.1_first_agent.py

cd "../9.webscan_app"
python app.py   # → http://localhost:5000
```
