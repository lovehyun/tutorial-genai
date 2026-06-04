# 프롬프트에서 에이전트까지: LLM 서비스 설계 종합

## 과정 정보
- **기간**: 5일 (총 40시간) | 심화 실습 추가 시 6~7일 확장 가능
- **난이도**: 중급~고급 (이론과 실습 병행)
- **대상**: Python과 API 호출 경험이 있고, LLM 기반 서비스 설계의 전체 그림을 한 번에 잡고 싶은 개발자
- **선수 과목**: Python 기초, REST API 이해, OpenAI API 사용 경험 권장

## 학습 목표
1. LLM 개념과 한계, 프롬프트 엔지니어링의 역할을 이해한다
2. 기본 프롬프트 구조(Persona, In-context Learning 등)와 고급 프롬프팅 전략(Plan-and-Solve, Self-Refine, ToT 등)을 학습한다
3. RAG의 역할과 핵심 파이프라인(Indexing → Search → Generation)을 이해하고 기본 구현을 실습한다
4. 프롬프트 보안 취약점(Jailbreak/Prompt Injection)과 방어 개념, 최신 트렌드(멀티모달/개인화/메모리)를 개괄한다
5. AI Service/Agent Design 관점에서 Agentic Workflow 구조와 아키텍처(Single, Tool-using, ReAct, HITL)를 이해한다
6. Workflow/Agent 디자인 패턴(Chaining, Routing, Parallelization, Orchestrator-Worker, Planning 등)을 적용 실습한다
7. Tool Calling, MCP 기반 도구 연동, Self-Correction Loop를 통해 실제 동작하는 워크플로우를 구현한다
8. Agentic RAG, Memory 관리(Short/Long Term), Safety/보안, Evaluation, AgentOps까지 개발-운영 관점의 핵심 요소를 한 번에 연결한다

---

## 커리큘럼

> 자료 표기: `0.docs/` = 강의 교안(이론), 그 외 = 실습 코드

### Day 1: LLM 이해와 프롬프트 엔지니어링

> 학습목표 1, 2 — LLM 개념/한계를 파악하고 기본~고급 프롬프팅 전략을 익힌다

| 시간 | 주제 | 자료 | 설명 |
|------|------|------|------|
| 09:00-09:30 | 오리엔테이션 | — | 5일 과정 로드맵, 환경 설정 |
| 09:30-10:30 | 생성형 AI 지형도 | `0.docs/01_genai_intro/01_genai_landscape.md` | AI 역사, LLM의 등장, 한계(환각/편향/컨텍스트) |
| | | `0.docs/01_genai_intro/02_llm_companies_models.md` | 주요 기업/모델 비교, 선택 기준 |
| 10:45-12:00 | 프롬프트 엔지니어링 기초~중급 | `0.docs/01_genai_intro/04_prompt_engineering.md` | Zero-Shot → Few-Shot → CoT → Zero-Shot CoT 진화 |
| | | `1.openai/1.intro/11.sdk_new.py` | [실습] OpenAI SDK로 프롬프트 패턴 직접 실행 |
| | | `2.langchain/2.prompts/1.basic/1.1_template_chat.py` | [실습] PromptTemplate 기본 구조 |
| | | `2.langchain/2.prompts/2.chat_templates/2.1_template_chat.py` | [실습] Persona 역할 분리 (ChatPromptTemplate) |
| 13:00-14:30 | 고급 프롬프팅 전략 | `0.docs/05_genai_advanced/04_prompt_engineering_code.md` | Plan-and-Solve, Self-Refine, Self-Consistency, ReAct, ToT |
| | | `2.langchain/2.prompts/2.chat_templates/2.2_template_chat_chaining.py` | [실습] 프롬프트 체이닝 |
| | | `2.langchain/5.tasks/0.legacy(instruct)/1.summarization_instruct.py` | [실습] 요약 프롬프트 패턴 |
| | | `2.langchain/5.tasks/0.legacy(instruct)/4.sqlgeneration_instruct.py` | [실습] SQL 생성 프롬프트 |
| 14:45-16:00 | Context Engineering | `0.docs/05_genai_advanced/05_context_engineering.md` | 시스템 프롬프트, 토큰 예산, RAG 컨텍스트, 메모리 통합 |
| | | `2.langchain/3.structured_output/3.pydantic_parser.py` | [실습] Pydantic 파서로 구조화된 출력 |
| | | `2.langchain/3.structured_output/4.with_structured_output.py` | [실습] with_structured_output |
| 16:00-17:00 | 종합 실습 & Q&A | `2.langchain/4.chaining/2.runnablelambda/2.4_runnablelambda_pii_mask.py` | [실습] 프롬프트 → 파서 → 후처리 전체 파이프라인, Day 1 정리 |

---

### Day 2: RAG 파이프라인과 프롬프트 보안

> 학습목표 3, 4 — RAG 핵심 구현을 실습하고, 보안 위협과 최신 트렌드를 파악한다

| 시간 | 주제 | 자료 | 설명 |
|------|------|------|------|
| 09:00-09:30 | Day 1 복습 | — | 프롬프트 엔지니어링 핵심 요약 |
| 09:30-10:30 | RAG 아키텍처 이론 | `0.docs/05_genai_advanced/06_rag_system.md` | Indexing → Search → Generation 파이프라인, 청킹 전략, 임베딩 |
| | | `12.study/6.embedding/1.tokenize_visualize.py` | [실습] 토큰화 과정 시각화 |
| | | `12.study/6.embedding/2.embedding_visualize.py` | [실습] 임베딩 벡터 공간 시각화 |
| 10:45-12:00 | RAG 기본 구현 (Indexing & Search) | `12.study/6.embedding/4.similarity_matrix.py` | [실습] 코사인 유사도 행렬 |
| | | `1.openai/7.rag/1.rag_basic.py` | [실습] FAISS 인덱스 생성과 검색 |
| | | `2.langchain/7.RAG/2.loaders/2.1_text_loader.py` | [실습] 텍스트 로드 |
| | | `2.langchain/7.RAG/3.vectorstore/3.1_persist.py` | [실습] ChromaDB 저장/로드 |
| 13:00-14:30 | RAG 기본 구현 (Generation & 웹앱) | `2.langchain/7.RAG/1.basics/1.3_first_rag.py` | [실습] Store & Retrieve 기본 RAG |
| | | `2.langchain/7.RAG/2.loaders/2.2_pdf_loader.py` | [실습] PDF 문서 로드 |
| | | `2.langchain/7.RAG/3.vectorstore/3.4_search_modes.py` | [실습] ChromaDB 유사도 검색 |
| | | `2.langchain/7.RAG/8.web_app/1.minimal/app.py` | [실습] RAG 웹 앱 구조 확인 |
| 14:45-15:45 | 프롬프트 보안 | `0.docs/05_genai_advanced/16_evaluation_safety.md` | Jailbreak 공격 유형, Prompt Injection 패턴, 방어 전략(가드레일) |
| 15:45-16:30 | 최신 트렌드 개괄 | `0.docs/05_genai_advanced/08_multimodal_ai.md` | 멀티모달(Vision/Audio/Video), 개인화, 메모리 트렌드 |
| | | `0.docs/01_genai_intro/05_so_what_now.md` | 프롬프트 엔지니어링의 현재와 미래 |
| 16:30-17:00 | Day 2 정리 & Q&A | — | RAG + 보안 핵심 복습, 질의응답 |

---

### Day 3: Agentic Workflow와 아키텍처

> 학습목표 5 — 에이전트 유형(Single → Tool-using → ReAct → HITL)을 이해하고 LangGraph로 구현한다

| 시간 | 주제 | 자료 | 설명 |
|------|------|------|------|
| 09:00-09:30 | Day 2 복습 | — | RAG/보안 핵심 요약 |
| 09:30-10:30 | AI 에이전트 개요 | `0.docs/05_genai_advanced/09_ai_agent_overview.md` | 챗봇 vs 파이프라인 vs 에이전트, 에이전트의 관찰-사고-행동 루프 |
| | | `2.langchain/8.agents/1.builtin_tools/1.0_list_all_tools.py` | [실습] 에이전트 기본 역량 탐색 |
| 10:45-11:15 | Single & Tool-using Agent | `2.langchain/8.agents/1.builtin_tools/1.1_llm_math.py` | [실습] llm-math(Calculator) 도구 에이전트 (현행 create_agent) |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/1.wikipedia/2.1_wikipedia1.py` | [실습] Wikipedia 검색 에이전트 |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.1_customtools1_add.py` | [실습] @tool 데코레이터로 커스텀 도구 생성 |
| 11:15-12:00 | ReAct 패턴 | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.3_customtools1_addmultiply2_final.py` | [실습] 도구 자동 선택 ReAct 에이전트 |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/6.1_decide_human_serper.py` | [실습] 도구 자동 판단 라우팅 |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/7.complex/8.1_complex.py` | [실습] 다중 도구 복합 에이전트 |
| 13:00-13:45 | Human-in-the-Loop (HITL) | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.1_humanagent.py` | [실습] 사람 개입 기본 |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.3_humanagent2_custom.py` | [실습] 커스텀 HITL |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.5_humanagent4_websearchmini.py` | [실습] HITL + 웹검색 결합 |
| 13:45-14:30 | LangGraph 기초 | `0.docs/05_genai_advanced/10_langgraph_agents.md` | StateGraph, 노드, 엣지, 조건부 분기 개념 |
| | | `2.langchain/9.langgraph/1.basic_graph.py` | [실습] 기본 StateGraph 생성 |
| 14:45-15:30 | LangGraph 실습 | `2.langchain/9.langgraph/2.memory_checkpointing.py` | [실습] 체크포인팅 |
| | | `2.langchain/9.langgraph/3.conditional_branching.py` | [실습] 조건부 분기 |
| | | `2.langchain/9.langgraph/4.tools_cyclic_graph.py` | [실습] 순환 그래프 |
| 15:30-17:00 | 에이전트 서비스 설계 | `0.docs/06_genai_applied/07_ai_agent_service.md` | 서비스 관점의 에이전트 아키텍처, 기술 스택 통합 |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.1_smartagent.py` | [실습] 스마트 에이전트 구현, Day 3 정리 |

---

### Day 4: 디자인 패턴과 도구 연동

> 학습목표 6, 7 — 5대 패턴을 적용하고, Tool Calling · MCP · Self-Correction을 구현한다

| 시간 | 주제 | 자료 | 설명 |
|------|------|------|------|
| 09:00-09:30 | Day 3 복습 | — | Agentic Workflow 핵심 요약 |
| 09:30-10:00 | 패턴 1: Prompt Chaining | `2.langchain/8.agents/9.agentic_patterns/9.1_prompt_chaining.py` | [실습] 프롬프트 순차 연결 패턴 |
| 10:00-10:30 | 패턴 2: Routing | `2.langchain/8.agents/9.agentic_patterns/9.2_routing.py` | [실습] 입력 기반 동적 분기 패턴 |
| 10:45-11:15 | 패턴 3: Parallelization | `2.langchain/8.agents/9.agentic_patterns/9.3_parallelization_eg1.py` | [실습] 독립 작업 병렬 실행 패턴 |
| 11:15-11:45 | 패턴 4: Orchestrator-Worker | `2.langchain/8.agents/9.agentic_patterns/9.4_orchestrator_worker.py` | [실습] 오케스트레이터의 작업 분배 패턴 |
| 11:45-12:00 | 패턴 5: Evaluator-Optimizer | `2.langchain/8.agents/9.agentic_patterns/9.5_evaluator_optimizer.py` | [실습] 평가 → 최적화 반복 패턴 |
| 13:00-13:45 | Tool Calling | `0.docs/05_genai_advanced/01_openai_advanced.md` | Function Calling, tool_calls, JSON Schema |
| | | `1.openai/9.structured_output/5.func_calling_basic.py` | [실습] OpenAI Function Calling |
| | | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.4_customtools2_getinfo.py` | [실습] 정보 조회 도구 |
| 13:45-14:30 | MCP 프로토콜 연동 | `0.docs/05_genai_advanced/12_mcp_model_context_protocol.md` | MCP 아키텍처, 서버/클라이언트, 전송 계층 |
| | | `8.mcp/1.common/1.intro/simple_server.py` | [실습] MCP 서버 구현 |
| | | `8.mcp/1.common/1.intro/5.simple_client.py` | [실습] MCP 클라이언트 연결 |
| 14:45-15:30 | MCP 에이전트 연동 | `8.mcp/2.openai/1.agent_tool/server.py` | [실습] 에이전트용 MCP 서버 |
| | | `8.mcp/2.openai/1.agent_tool/3.client_gpt.py` | [실습] GPT 기반 MCP 에이전트 |
| | | `8.mcp/4.langchain/2.langchain_bridge/mcp_bridge.py` | [실습] MCP → LangChain 브릿지 |
| 15:30-16:15 | Self-Correction Loop | `2.langchain/9.langgraph/6.self_correction_loop.py` | [실습] 출력 검증 → 자동 수정 반복 패턴 |
| | | `2.langchain/9.langgraph/5.state_debugging.py` | [실습] 그래프 상태 디버깅 |
| 16:15-17:00 | 종합 실습 | `2.langchain/9.langgraph/10.customtools1_addmultiply_langgraph.py` | [실습] 패턴 + 도구 + Self-Correction 결합, Day 4 정리 |

---

### Day 5: 통합 — Agentic RAG부터 AgentOps까지

> 학습목표 8 — 개발-운영 관점의 핵심 요소를 하나의 워크플로우로 연결한다

| 시간 | 주제 | 자료 | 설명 |
|------|------|------|------|
| 09:00-09:30 | Day 4 복습 | — | 패턴/도구/MCP 핵심 요약 |
| 09:30-10:30 | Agentic RAG | `0.docs/06_genai_applied/01_document_qa_chatbot.md` | 일반 RAG vs Agentic RAG, 자율 검색 판단 |
| | | `2.langchain/7.RAG/6.agentic/6.1_agentic_rag.py` | [실습] 에이전트가 검색을 자율 판단하는 Agentic RAG |
| | | `2.langchain/7.RAG/8.web_app/2.file_append/app.py` | [실습] 동적 문서 관리 RAG 앱 |
| 10:45-11:30 | Memory 관리 (Short-term / Long-term) | `2.langchain/6.memory/1.nomemory/1.2_nomemory.py` | [실습] 메모리 없는 대화의 한계 체험 |
| | | `2.langchain/6.memory/3.sessions/3.1_history.py` | [실습] Short-term: 세션 내 대화 메모리 |
| | | `2.langchain/6.memory/2.storage/2.3_sqlite.py` | [실습] Long-term: SQLite 영구 메모리 |
| | | `2.langchain/6.memory/4.compression/4.3_summary_session.py` | [실습] 대화 요약으로 컨텍스트 압축 |
| 11:30-12:00 | LangGraph 메모리 통합 | `2.langchain/6.memory/6.langgraph/6.1_memory_saver.py` | [실습] LangGraph 기반 메모리 |
| | | `2.langchain/6.memory/6.langgraph/6.2_with_summary.py` | [실습] LangGraph 요약 메모리 |
| 13:00-13:45 | Safety & 보안 심화 | `0.docs/05_genai_advanced/16_evaluation_safety.md` | 가드레일 구현, 콘텐츠 필터링, LLM-as-Judge |
| | | `8.mcp/4.langchain/3.tools_safety/server.py` | [실습] 도구 안전성 서버 |
| | | `8.mcp/4.langchain/3.tools_safety/2.client2_restrict.py` | [실습] 도구 접근 제한 |
| 13:45-14:30 | Evaluation | `0.docs/05_genai_advanced/16_evaluation_safety.md` | 참조 기반/참조 없는/LLM-as-Judge 평가 프레임워크 |
| | | `0.docs/06_genai_applied/07_ai_agent_service.md` | 에이전트 서비스 평가 기준, 신뢰성 설계 |
| 14:45-15:15 | AgentOps & 모니터링 | `2.langchain/9.langgraph/7.agentops_monitoring.py` | [실습] 에이전트 실행 모니터링, 비용/지연/성공률 추적 |
| 15:15-16:00 | 멀티에이전트 통합 | `10.project/10.ai_agent/app6_multi_agent.py` | [실습] 역할 분리 멀티에이전트 |
| | | `10.project/10.ai_agent/app8_multi_agent3_final.py` | [실습] 완성형 멀티에이전트 시스템 |
| 16:00-17:00 | 전체 과정 종합 | — | 5일 핵심 요약, 아키텍처 설계 워크숍, Q&A |

---

## Day별 학습목표 매핑

| Day | 학습목표 | 핵심 키워드 |
|-----|---------|------------|
| 1 | 1, 2 | LLM 한계, Persona, ICL, Few-Shot, CoT, Plan-and-Solve, Self-Refine, ToT, Context Engineering |
| 2 | 3, 4 | Indexing, Search, Generation, FAISS, ChromaDB, Jailbreak, Prompt Injection, 멀티모달 트렌드 |
| 3 | 5 | Single Agent, Tool-using, ReAct, HITL, LangGraph StateGraph, 순환/분기 |
| 4 | 6, 7 | Chaining, Routing, Parallelization, Orchestrator-Worker, Tool Calling, MCP, Self-Correction |
| 5 | 8 | Agentic RAG, Short/Long-term Memory, Safety, Evaluation, AgentOps, Multi-Agent |

## 6~7일 확장 가이드

| 확장 Day | 내용 | 추가 자료 |
|----------|------|-----------|
| Day 6 | MCP 심화 — 멀티 도구 서버, LangGraph 브릿지, Claude Desktop 연동 | `8.mcp/2.openai/2.multi_tools/`, `8.mcp/3.anthropic/1.claude_desktop/` |
| Day 7 | 캡스톤 프로젝트 — 5일간 학습을 결합한 자유 주제 개발 + 발표 | `10.project/` 전체 참조 |

## 환경 설정

```bash
pip install openai anthropic google-generativeai langchain langchain-openai langchain-anthropic langchain-community langgraph chromadb faiss-cpu flask mcp agentops
```

## 참고 자료

### 교안 (이론)
- `0.docs/01_genai_intro/01_genai_landscape.md` — 생성형 AI 지형도
- `0.docs/01_genai_intro/04_prompt_engineering.md` — 프롬프트 엔지니어링 진화
- `0.docs/05_genai_advanced/04_prompt_engineering_code.md` — 고급 프롬프팅 구현
- `0.docs/05_genai_advanced/05_context_engineering.md` — Context Engineering
- `0.docs/05_genai_advanced/06_rag_system.md` — RAG 시스템 아키텍처
- `0.docs/05_genai_advanced/08_multimodal_ai.md` — 멀티모달 AI
- `0.docs/05_genai_advanced/09_ai_agent_overview.md` — AI 에이전트 개요
- `0.docs/05_genai_advanced/10_langgraph_agents.md` — LangGraph 에이전트
- `0.docs/05_genai_advanced/12_mcp_model_context_protocol.md` — MCP 프로토콜
- `0.docs/05_genai_advanced/16_evaluation_safety.md` — 평가와 안전성
- `0.docs/06_genai_applied/01_document_qa_chatbot.md` — 문서 QA 챗봇
- `0.docs/06_genai_applied/07_ai_agent_service.md` — AI 에이전트 서비스

### 실습 코드
- `1.openai/` — OpenAI API, FAISS RAG
- `2.langchain/2.prompts/` — 프롬프트 템플릿
- `2.langchain/3.structured_output/` — 출력 파서
- `2.langchain/4.chaining/` — LCEL 체이닝
- `2.langchain/6.memory/` — 메모리 관리
- `2.langchain/7.RAG/` — RAG 파이프라인
- `2.langchain/8.agents/` — 에이전트
- `2.langchain/9.langgraph/` — LangGraph
- `2.langchain/8.agents/9.agentic_patterns/` — 5대 Agentic 패턴
- `8.mcp/` — MCP 프로토콜
- `12.study/6.embedding/` — 임베딩 시각화
- `10.project/10.ai_agent/` — 멀티에이전트 프로젝트
