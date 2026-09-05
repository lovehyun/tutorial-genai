# 2단계 → 3단계 변경점 (변형 a — 순차/안전)

이 폴더는 3단계의 세 변형(`a.sequential` / `b.parallel_unsafe` / `c.parallel_guarded`) 중
`a` 다 — [`../README.md`](../README.md) 참고. `b.parallel_unsafe/CHANGES.md`에 있는
2→3단계 공통 변경(메인/워커 분리, 백그라운드 위임, `asyncio.Event`)은 그대로 적용된다.
여기서는 `a` 고유의 차이만 적는다.

## `b.parallel_unsafe/` 대비 바뀐 것 — 딱 한 군데

```python
# [3a] 미들웨어 — 워커가 한 턴에 도구를 하나만 요청하도록 강제
@wrap_model_call
def one_tool_call_per_turn(request, handler):
    request.model_settings = {**request.model_settings, "parallel_tool_calls": False}
    return handler(request)

worker_agent = create_agent(
    llm, tools,
    system_prompt=WORKER_SYSTEM,
    checkpointer=checkpointer,
    interrupt_before=["tools"],
    middleware=[one_tool_call_per_turn],   # ← 이 한 줄
)
```

## 왜 `llm.bind(parallel_tool_calls=False)` 를 미리 걸어두면 안 되는가

`create_agent()`는 내부적으로 매번 `model.bind_tools(tools, **model_settings)`를 다시 호출한다
(`langchain/agents/factory.py`). 이미 `.bind()`로 감싸둔 모델에 `.bind_tools()`를 또 부르면,
`_ChatModelBinding`이 원본 모델로 위임해서 새로 바인딩을 만들기 때문에 미리 걸어둔
`parallel_tool_calls=False`가 조용히 사라진다 — 직접 확인했다:

```python
bound = llm.bind(parallel_tool_calls=False)
bound.bind_tools([]).kwargs   # {'tools': []}  ← parallel_tool_calls 가 없다!
```

`model_settings`는 `create_agent()`의 top-level 파라미터로 노출돼 있지 않고, `wrap_model_call`
미들웨어가 매 모델 호출 직전에 `request.model_settings`를 고쳐 쓸 수 있는 유일한 공식 통로다.

## 효과

`interrupt_before=["tools"]`는 "AI 턴 하나"마다 멈춘다. 턴마다 도구가 하나뿐이면
"도구 하나 = 승인 카드 하나"가 항상 성립한다 — `b`에서 봤던 "여러 도구가 한 카드에
몰려서 뜨는" 문제가 구조적으로 생기지 않는다.

## 한계 → 여기서 끝이 아니다

대신 온보딩 하나(계정생성·email·vpn·메일)에 승인이 4번 필요하다. 안전하지만
승인 피로가 그대로 남는다 — `c.parallel_guarded/`가 "병렬은 유지하되 위험한 것만
따로 승인받는" 절충안을 보여준다.
