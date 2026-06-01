# Agentic 디자인 패턴

Anthropic이 제시한 5대 Agentic 디자인 패턴을 LangChain/LangGraph로 구현한 예제 모음입니다.

> 참고: [Building effective agents (Anthropic, 2024)](https://www.anthropic.com/research/building-effective-agents)

## 핵심 개념

Agentic 시스템은 LLM이 단순 질의응답을 넘어 **자율적으로 판단하고 행동**하는 시스템입니다. Anthropic은 복잡한 프레임워크 대신 **단순한 조합 가능한 패턴**을 권장합니다.

```
┌─────────────────────────────────────────────────────────┐
│                  Agentic 시스템 스펙트럼                    │
│                                                         │
│  Workflows (예측 가능)          Agents (자율적)            │
│  ├── Prompt Chaining            ├── Evaluator-Optimizer  │
│  ├── Routing                    └── Autonomous Agent     │
│  ├── Parallelization                                     │
│  └── Orchestrator-Worker                                 │
└─────────────────────────────────────────────────────────┘
```

## 5대 패턴 요약

| # | 패턴 | 핵심 아이디어 | 구조 |
|---|------|-------------|------|
| 1 | **Prompt Chaining** | 순차 파이프라인 + 게이트 검증 | A → Gate → B → C |
| 2 | **Routing** | 입력 분류 → 전문 체인 분기 | Classifier → {Chain A, B, C} |
| 3 | **Parallelization** | 팬아웃/팬인 + 투표 | Input → [A, B, C] → Aggregate |
| 4 | **Orchestrator-Worker** | 동적 작업 분해·위임·종합 | Orchestrator → Workers → Synthesizer |
| 5 | **Evaluator-Optimizer** | 생성→평가→개선 반복 루프 | Generator ⇄ Evaluator |

## 예제 목록

| 파일 | 패턴 | 설명 | 주요 기술 |
|------|------|------|----------|
| `9.1_prompt_chaining.py` | Prompt Chaining | 리서치→게이트→분석→보고서 파이프라인 | LCEL 체인 |
| `9.2_routing.py` | Routing | 고객 문의 분류 → 전문 체인 분기 | RunnableLambda |
| `9.3_parallelization.py` | Parallelization | 다관점 분석 + 투표 패턴 | RunnableParallel |
| `9.4_orchestrator_worker.py` | Orchestrator-Worker | 동적 작업 분해 및 워커 위임 | LangGraph StateGraph |
| `9.5_evaluator_optimizer.py` | Evaluator-Optimizer | 마케팅 카피 생성→평가→개선 루프 | LangGraph 순환 그래프 |

## 패턴 비교

### Prompt Chaining vs Orchestrator-Worker

| 비교 항목 | Prompt Chaining | Orchestrator-Worker |
|----------|----------------|-------------------|
| 작업 분해 | 사전에 고정 | 실행 시 동적 결정 |
| 단계 수 | 고정 | 입력에 따라 가변 |
| 복잡도 | 낮음 | 높음 |
| 사용 시점 | 단계가 명확할 때 | 작업 범위가 불확실할 때 |

### Parallelization vs Orchestrator-Worker

| 비교 항목 | Parallelization | Orchestrator-Worker |
|----------|----------------|-------------------|
| 작업 정의 | 사전에 고정 | LLM이 동적으로 결정 |
| 실행 방식 | 동시 실행 | 순차 또는 동시 |
| 종합 방식 | 단순 집계/투표 | LLM이 종합 |

## 패턴 선택 가이드

```
작업이 명확한 단계로 나뉘는가?
├── Yes → 단계 간 검증이 필요한가?
│         ├── Yes → Prompt Chaining
│         └── No  → 단계들이 독립적인가?
│                   ├── Yes → Parallelization
│                   └── No  → Prompt Chaining
└── No  → 입력 유형에 따라 처리가 달라지는가?
          ├── Yes → Routing
          └── No  → 반복적 개선이 필요한가?
                    ├── Yes → Evaluator-Optimizer
                    └── No  → Orchestrator-Worker
```

## 설치

```bash
pip install langchain langchain-openai langgraph python-dotenv
```

## 학습 경로

1. **기초**: Prompt Chaining → Routing (1~2번)
2. **중급**: Parallelization (3번)
3. **고급**: Orchestrator-Worker → Evaluator-Optimizer (4~5번)
