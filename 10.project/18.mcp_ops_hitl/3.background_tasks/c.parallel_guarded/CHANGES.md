# 2단계 → 3단계 변경점 (변형 c — 병렬 계획 + 개별 승인)

이 폴더는 3단계의 세 변형(`a.sequential` / `b.parallel_unsafe` / `c.parallel_guarded`) 중
`c` 다 — [`../README.md`](../README.md) 참고. `b.parallel_unsafe/CHANGES.md`에 있는
2→3단계 공통 변경(메인/워커 분리, 백그라운드 위임, `asyncio.Event`)은 그대로 적용된다.
여기서는 `c` 고유의 차이만 적는다.

## `b.parallel_unsafe/` 대비 바뀐 것 — `run_job()`의 승인 처리 방식

`a`/`b`는 LangGraph의 `tools` 노드가 이 턴의 `tool_calls`를 통째로 실행하게 두고,
거부할 때만 `as_node="tools"`로 끼어들었다. `c`는 이 턴의 `tool_calls`를
**우리가 처음부터 하나씩** 직접 처리한다:

```python
results = {}   # tool_call_id -> ToolMessage

for c in calls:
    if c["name"] in SAFE_TOOLS:
        results[c["id"]] = await _invoke_tool(c)      # 안전 — 바로 실행
        continue

    job["pending"] = [{"name": c["name"], "args": c["args"]}]   # ← 이 호출 '하나만'
    ...위 대기 로직...
    results[c["id"]] = (
        await _invoke_tool(c) if approved
        else ToolMessage(content="거부됨", tool_call_id=c["id"], name=c["name"])
    )

# 이 턴의 모든 tool_call_id 에 결과가 모이면 한 번에 주입 — tools 노드는 안 불린다
await worker.aupdate_state(config, {"messages": [results[c["id"]] for c in calls]},
                            as_node="tools")
state = await worker.ainvoke(None, config=config)
```

`_invoke_tool()`은 `tool.ainvoke(call["args"])`로 도구를 직접 부른다 — `ToolNode`가
내부적으로 하는 일과 같다([`5.mcp/4.langchain/2.langchain_agent/1.1_client1_pydantic.py`]
(../../../../5.mcp/4.langchain/2.langchain_agent/1.1_client1_pydantic.py)에도 같은 패턴이 있다).

## 왜 이게 `a`보다 빠른가

`a`는 `parallel_tool_calls=False`로 모델이 **한 턴에 도구 하나만** 계획하게 강제한다 —
안전하지만, 승인할 때마다 모델을 다시 불러 "다음엔 뭘 할까"를 새로 물어야 한다
(온보딩 하나에 모델 호출이 4번 이상 걸릴 수 있다).

`c`는 모델의 병렬 계획(빠름)은 그대로 두고, **우리 쪽에서** 그 배치를 쪼갠다. 모델은
"계정생성·email·vpn·메일"을 한 번에 다 계획해서 던지고, 우리가 그걸 순서대로
하나씩 승인받아 실행한다 — 모델 왕복은 한 번, 승인 카드는 여전히 하나씩.

## 한계

- 안전한 도구(`SAFE_TOOLS`)를 승인 대기 없이 즉시 실행하는 것까지는 `a`/`b`와 같다.
  다만 `c`는 그 실행을 **직접** 하므로(그래프의 `tools` 노드를 안 거치므로), MCP 도구가
  아닌 로컬 `@tool`(`delegate_task`/`list_jobs`)이 워커에 섞이는 구조로 바뀌면
  `TOOLS_BY_NAME` 조회가 깨지지 않도록 신경 써야 한다 — 지금은 워커에 MCP 도구만 있어서 문제 없다.
- 도구 실행 중 예외가 나면 `_invoke_tool()`이 에러 메시지를 `ToolMessage` 로 감싸 돌려준다
  (그래프가 대신 처리해 주던 재시도·에러 포맷팅은 없다) — 데모 범위 밖.
