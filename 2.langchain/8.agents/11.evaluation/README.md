# 에이전트 평가 (Evaluation)

에이전트는 **비결정적**이라 "한 번 돌려보니 되더라" 로는 회귀를 못 잡습니다.
프롬프트/모델/도구를 바꿀 때마다 핵심 시나리오가 여전히 통과하는지 자동으로 확인해야 합니다.

| 파일 | 무엇을 평가하나 |
|---|---|
| `11.1_tool_call_eval.py` | **도구 선택 정확도** — 불러야 할 때 부르고, 아닐 때 안 부르는가 (외부 의존성 없음) |

## 평가의 단계 (쉬운 → 어려운)

1. **도구 선택** — 의도한 도구를 골랐는가 ← 여기서 시작 (`11.1`)
2. **도구 인자** — 인자까지 맞는가 (예: `city == "서울"`)
3. **최종 답변 품질** — LLM-as-judge 로 채점 ([`../9.agentic_patterns/9.3_parallelization_eg2.py`](../9.agentic_patterns/))
4. **데이터셋·리포트 자동화** — LangSmith Evaluations / `agentevals`

## 팁

- `temperature=0` 으로 두면 평가 재현성이 올라갑니다.
- 상태/메시지 흐름 디버깅은 [`../5.langgraph_memory/5.3_inspect_state.py`](../5.langgraph_memory/) 와 함께 보면 좋습니다.
