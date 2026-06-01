# Agentic 아키텍처 설계

## 과정 정보
- **기간**: 5일 (총 40시간)
- **난이도**: 고급
- **대상**: LangGraph와 Agentic 패턴을 학습한 후 멀티에이전트 시스템을 설계하고 싶은 개발자
- **선수 과목**: 중급 3. LangGraph & Agentic 패턴

## 학습 목표
1. LangGraph의 모든 고급 기능(순환, 분기, 체크포인팅, Self-Correction)을 능숙하게 활용할 수 있다
2. 5대 Agentic 패턴을 실전 시나리오에 적용하고 조합할 수 있다
3. MCP 기반 도구 연동과 멀티에이전트 아키텍처를 설계할 수 있다
4. 복합 에이전트 시스템을 직접 설계하고 캡스톤 프로젝트로 완성할 수 있다

## 커리큘럼

### Day 1: LangGraph 심화

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 5일 과정 로드맵, Agentic 아키텍처 개요 |
| 09:30-10:00 | StateGraph 복습 | `2.langchain/9.langgraph/1.basic_graph.py` | StateGraph 기본 구조 재확인 |
| 10:00-10:30 | 체크포인팅 심화 | `2.langchain/9.langgraph/2.memory_checkpointing.py` | 상태 저장/복원, 중단점 재개 |
| 10:45-11:15 | 조건부 분기 심화 | `2.langchain/9.langgraph/3.conditional_branching.py` | 다중 조건, 중첩 분기 패턴 |
| 11:15-12:00 | 순환 그래프 심화 | `2.langchain/9.langgraph/4.tools_cyclic_graph.py` | 도구 호출 순환, 종료 조건 설계 |
| 13:00-13:30 | 상태 디버깅 | `2.langchain/9.langgraph/5.state_debugging.py` | 복잡한 그래프의 상태 추적 |
| 13:30-14:00 | Self-Correction 심화 | `2.langchain/9.langgraph/6.self_correction_loop.py` | 다단계 검증 + 자동 수정 |
| 14:00-14:30 | AgentOps 모니터링 | `2.langchain/9.langgraph/7.agentops_monitoring.py` | 프로덕션 수준 모니터링 |
| 14:45-15:30 | 커스텀 도구 + LangGraph | `2.langchain/9.langgraph/10.customtools1_addmultiply_langgraph.py` | 기존 도구의 그래프 전환 패턴 |
| 15:30-17:00 | 실습: 복잡한 워크플로우 설계 | — | 5개 이상 노드를 가진 그래프 직접 설계 |

### Day 2: 5대 Agentic 패턴 실전 적용

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | LangGraph 심화 복습 |
| 09:30-10:30 | Prompt Chaining 실전 | `2.langchain/8.agents/9.agentic_patterns/9.1_prompt_chaining.py` | 실전 시나리오: 문서 분석 → 요약 → 번역 체이닝 |
| 10:45-11:30 | Routing 실전 | `2.langchain/8.agents/9.agentic_patterns/9.2_routing.py` | 실전 시나리오: 질문 유형별 전문가 에이전트 라우팅 |
| 11:30-12:00 | Parallelization 실전 | `2.langchain/8.agents/9.agentic_patterns/9.3_parallelization.py` | 실전 시나리오: 다중 소스 동시 분석 |
| 13:00-13:45 | Orchestrator-Worker 실전 | `2.langchain/8.agents/9.agentic_patterns/9.4_orchestrator_worker.py` | 실전 시나리오: 복합 작업 분배 시스템 |
| 13:45-14:30 | Evaluator-Optimizer 실전 | `2.langchain/8.agents/9.agentic_patterns/9.5_evaluator_optimizer.py` | 실전 시나리오: 코드 생성 → 테스트 → 수정 반복 |
| 14:45-15:30 | 패턴 조합 설계 | — | 2개 이상 패턴을 결합한 아키텍처 설계 워크숍 |
| 15:30-17:00 | 설계 발표 & 피드백 | — | 팀별 아키텍처 발표, 상호 리뷰 |

### Day 3: MCP 도구 연동 에이전트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | Agentic 패턴 복습 |
| 09:30-10:00 | MCP 서버/클라이언트 복습 | `4.anthropic/3.mcp/1.intro/simple_server.py`, `4.anthropic/3.mcp/1.intro/5.simple_client.py` | MCP 기본 구조 재확인 |
| 10:00-10:30 | MCP 에이전트 도구 | `4.anthropic/3.mcp/2.agents/1.agent_tool/server.py`, `4.anthropic/3.mcp/2.agents/1.agent_tool/3.client_gpt.py` | MCP 기반 에이전트 도구 |
| 10:45-11:15 | MCP 멀티 도구 | `4.anthropic/3.mcp/2.agents/2.multi_tools/math_server.py`, `4.anthropic/3.mcp/2.agents/2.multi_tools/2.smart_client_gpt.py` | 다중 MCP 서버 통합 |
| 11:15-12:00 | LangChain 브릿지 | `4.anthropic/3.mcp/4.langchain_bridge/mcp_bridge.py`, `4.anthropic/3.mcp/4.langchain_bridge/3.langgraph_agent_demo.py` | MCP ↔ LangGraph 브릿지 |
| 13:00-13:30 | 도구 안전성 | `4.anthropic/3.mcp/5.langchain_tools_safety/server.py`, `4.anthropic/3.mcp/5.langchain_tools_safety/2.client2_restrict.py` | 도구 접근 제한 설계 |
| 13:30-14:00 | 파일시스템 에이전트 | `4.anthropic/3.mcp/10.project_local/2.filesystem_client/3.fs_mcp_client3_gpt.py` | 파일 시스템 조작 에이전트 |
| 14:00-14:30 | 웹 스캔 에이전트 | `2.langchain/8.agents/10.mini_apps/1.webscan_app/app.py` | 웹 스캔 에이전트 |
| 14:45-15:30 | 스마트 에이전트 라우터 | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.2_smartagent_router.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.3_smartagent_router2_moretools.py` | 지능형 도구 라우팅 시스템 |
| 15:30-17:00 | 실습: MCP 기반 에이전트 설계 | — | 커스텀 MCP 서버 + LangGraph 에이전트 구축 |

### Day 4: 멀티에이전트 시스템

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 3 복습 | — | MCP 에이전트 복습 |
| 09:30-10:00 | AI 에이전트 기초 | `10.project/10.ai_agent/app.py`, `10.project/10.ai_agent/app2_history.py` | 프로젝트 수준 에이전트 분석 |
| 10:00-10:30 | 메타데이터 & 수학 에이전트 | `10.project/10.ai_agent/app3_metadata.py`, `10.project/10.ai_agent/app4_math.py` | 메타데이터 추적, 수학 전문 에이전트 |
| 10:45-11:15 | 복합 수학 에이전트 | `10.project/10.ai_agent/app5_mathcomplex.py` | 복잡한 수학 문제 해결 에이전트 |
| 11:15-12:00 | 멀티에이전트 (기초) | `10.project/10.ai_agent/app6_multi_agent.py` | 역할 분리 멀티에이전트 |
| 13:00-13:45 | 멀티에이전트 (심화) | `10.project/10.ai_agent/app7_multi_agent2.py`, `10.project/10.ai_agent/app8_multi_agent3_final.py` | 완성형 멀티에이전트 시스템 |
| 13:45-14:30 | 에이전트 챗봇 분석 | `10.project/1.chatbot_gui_agents/agents/agent_manager.py`, `10.project/1.chatbot_gui_agents/agents/memory_agent.py` | 에이전트 매니저 패턴 |
| 14:45-15:30 | 에이전트 모듈 설계 | `10.project/1.chatbot_gui_agents/agents/calculation_agent.py`, `10.project/1.chatbot_gui_agents/agents/search_agent.py` | 전문 에이전트 모듈 분리 패턴 |
| 15:30-17:00 | 캡스톤 프로젝트 설계 | — | Day 5 캡스톤을 위한 아키텍처 설계, 팀 구성 |

### Day 5: 캡스톤 프로젝트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 4 복습 & 캡스톤 안내 | — | 캡스톤 요구사항, 평가 기준 |
| 09:30-12:00 | 캡스톤 개발 (오전) | — | LangGraph + Agentic 패턴 + MCP를 조합한 자유 프로젝트 개발 |
| 13:00-15:00 | 캡스톤 개발 (오후) | — | 프로젝트 개발 계속, 멘토 피드백 |
| 15:00-16:00 | 캡스톤 발표 | — | 팀별/개인 프로젝트 발표 (10분/팀) |
| 16:00-17:00 | 전체 과정 회고 & 수료 | — | 5일간 학습 정리, 향후 학습 로드맵, 수료식 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-anthropic langgraph anthropic mcp agentops flask
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/09_ai_agent_overview.md` | AI 에이전트 개요 |
| `0.docs/05_genai_advanced/10_langgraph_agents.md` | LangGraph 에이전트 |
| `0.docs/05_genai_advanced/11_agentic_design_patterns.md` | 5대 Agentic 디자인 패턴 |
| `0.docs/05_genai_advanced/12_mcp_model_context_protocol.md` | MCP 프로토콜 |
| `0.docs/05_genai_advanced/16_evaluation_safety.md` | 평가와 안전성 |

## 참고 자료
- `2.langchain/9.langgraph/` — LangGraph 전체
- `2.langchain/8.agents/9.agentic_patterns/` — 5대 Agentic 패턴
- `2.langchain/8.agents/` — LangChain 에이전트
- `4.anthropic/3.mcp/` — MCP 프로토콜 전체
- `10.project/10.ai_agent/` — AI 에이전트 프로젝트
- `10.project/1.chatbot_gui_agents/` — 에이전트 챗봇
