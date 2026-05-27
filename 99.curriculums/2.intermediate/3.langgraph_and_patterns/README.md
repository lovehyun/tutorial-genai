# LangGraph & Agentic 패턴

## 과정 정보
- **기간**: 2일 (총 16시간)
- **난이도**: 중급
- **대상**: LangChain 에이전트 개발 경험이 있고 그래프 기반 워크플로우를 학습하려는 개발자
- **선수 과목**: 중급 2. AI 에이전트 개발

## 학습 목표
1. LangGraph의 StateGraph, 노드, 엣지 개념을 이해하고 구현할 수 있다
2. 순환 그래프, 조건부 분기, Self-Correction 패턴을 설계할 수 있다
3. 5대 Agentic 디자인 패턴(Prompt Chaining, Routing, Parallelization, Orchestrator-Worker, Evaluator-Optimizer)을 이해하고 적용할 수 있다

## 커리큘럼

### Day 1: LangGraph 기초와 고급 그래프

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | LangGraph 아키텍처, 기존 에이전트와의 차이 |
| 09:30-10:00 | 기본 그래프 | `2.langchain/8.langgraph/1.basic_graph.py` | StateGraph 생성, 노드/엣지 정의 |
| 10:00-10:30 | 메모리 & 체크포인팅 | `2.langchain/8.langgraph/2.memory_checkpointing.py` | 상태 저장 및 복원 메커니즘 |
| 10:45-11:15 | 조건부 분기 | `2.langchain/8.langgraph/3.conditional_branching.py` | 조건에 따른 동적 라우팅 |
| 11:15-12:00 | 도구 순환 그래프 | `2.langchain/8.langgraph/4.tools_cyclic_graph.py` | 도구 호출 → 결과 분석 → 재호출 순환 |
| 13:00-13:30 | 상태 디버깅 | `2.langchain/8.langgraph/5.state_debugging.py` | 그래프 상태 추적 및 디버깅 기법 |
| 13:30-14:00 | Self-Correction 루프 | `2.langchain/8.langgraph/6.self_correction_loop.py` | 출력 검증 → 자동 수정 반복 패턴 |
| 14:00-14:30 | AgentOps 모니터링 | `2.langchain/8.langgraph/7.agentops_monitoring.py` | 에이전트 실행 모니터링 |
| 14:45-15:30 | 커스텀 도구 + LangGraph | `2.langchain/8.langgraph/10.customtools1_addmultiply_langgraph.py` | 기존 커스텀 도구를 LangGraph로 전환 |
| 15:30-17:00 | 실습: 그래프 워크플로우 설계 | — | 나만의 조건부 분기 + Self-Correction 그래프 구축 |

### Day 2: 5대 Agentic 디자인 패턴

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | LangGraph 핵심 복습 |
| 09:30-10:30 | 패턴 1: Prompt Chaining | `2.langchain/9.agentic_patterns/1.prompt_chaining.py` | 프롬프트를 순차적으로 연결하는 패턴 |
| 10:45-11:30 | 패턴 2: Routing | `2.langchain/9.agentic_patterns/2.routing.py` | 입력에 따라 다른 경로로 분기하는 패턴 |
| 11:30-12:00 | 패턴 3: Parallelization | `2.langchain/9.agentic_patterns/3.parallelization.py` | 독립 작업을 병렬로 실행하는 패턴 |
| 13:00-13:45 | 패턴 4: Orchestrator-Worker | `2.langchain/9.agentic_patterns/4.orchestrator_worker.py` | 오케스트레이터가 워커에게 작업을 분배하는 패턴 |
| 13:45-14:30 | 패턴 5: Evaluator-Optimizer | `2.langchain/9.agentic_patterns/5.evaluator_optimizer.py` | 평가자가 결과를 평가하고 최적화하는 패턴 |
| 14:45-15:30 | 패턴 비교 분석 | — | 5대 패턴의 적용 시나리오 비교, 선택 가이드 |
| 15:30-17:00 | 종합 프로젝트 & 발표 | — | 패턴을 조합한 에이전트 워크플로우 설계 및 발표 |

## 환경 설정

```bash
pip install langchain langchain-openai langgraph agentops
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/10_langgraph_agents.md` | LangGraph 에이전트 (StateGraph, 순환, 분기) |
| `0.docs/05_genai_advanced/11_agentic_design_patterns.md` | 5대 Agentic 디자인 패턴 |

## 참고 자료
- `2.langchain/8.langgraph/` — LangGraph 예제 전체
- `2.langchain/9.agentic_patterns/` — 5대 Agentic 패턴
