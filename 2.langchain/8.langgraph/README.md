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
| `10.customtools1_addmultiply_langgraph.py` | 커스텀 도구 + LangGraph 통합 |

## 설치

```bash
pip install langgraph langchain langchain-openai
```

## 학습 경로

1. **기초**: 그래프 구조 → 메모리 → 조건 분기 (1~3번)
2. **중급**: 도구 통합 → 디버깅 (4~5번)
3. **응용**: 커스텀 도구 통합 (10번)
