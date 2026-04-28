# LangGraph 예제

LangGraph를 활용한 상태 기반 AI 에이전트 구축 예제 모음입니다.

## 예제 목록

### 기초
| 파일 | 설명 |
|------|------|
| `1.basic_graph.py` | 기본 그래프 구조 이해 |
| `2.memory_checkpointing.py` | 메모리 및 체크포인팅 |
| `3.conditional_branching.py` | 조건부 브랜칭 |

### 중급
| 파일 | 설명 |
|------|------|
| `4.tools_cyclic_graph.py` | 도구 사용과 순환 그래프 |
| `5.state_debugging.py` | 상태 및 스트리밍 디버깅 |

### 응용
| 파일 | 설명 |
|------|------|
| `6.self_correction_loop.py` | Self-Correction 루프 (생성→검증→피드백→재생성) |
| `7.agentops_monitoring.py` | AgentOps 모니터링 (토큰/비용/레이턴시 추적 + LangSmith) |
| `10.customtools1_addmultiply_langgraph.py` | 커스텀 도구 + LangGraph 통합 |

## Self-Correction Loop

LLM 출력을 자동으로 검증하고 개선하는 순환 패턴입니다.

```
START → 생성(Generator) → 검증(Validator)
                ↑                 │
                │    FAIL         │ PASS
                └─────────────────┘──→ END
```

- **생성 노드**: 코드/텍스트를 생성하거나 피드백을 반영하여 수정
- **검증 노드**: 품질 기준에 따라 PASS/FAIL 판정 + 피드백 생성
- **종료 조건**: 검증 통과(PASS) 또는 최대 반복 횟수 도달

## AgentOps 모니터링

프로덕션 LLM 애플리케이션의 운영 모니터링 방법입니다.

| 방법 | 설명 |
|------|------|
| **커스텀 콜백** | `BaseCallbackHandler`를 상속하여 토큰/비용/레이턴시 추적 |
| **LangSmith** | 환경변수 설정만으로 자동 트레이싱 (공식 관측성 플랫폼) |

## 설치

```bash
pip install langgraph langchain langchain-openai
```

## 학습 경로

1. **기초**: 그래프 구조 → 메모리 → 조건 분기 (1~3번)
2. **중급**: 도구 통합 → 디버깅 (4~5번)
3. **응용**: Self-Correction → AgentOps → 커스텀 도구 (6~7, 10번)
