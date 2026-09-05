# 2단계 → 3단계 변경점 (변형 b — 병렬/위험)

업무를 백그라운드 담당자(서브에이전트)에게 맡기고, 대화는 계속한다.

> 이 폴더는 3단계의 세 변형(`a.sequential` / `b.parallel_unsafe` / `c.parallel_guarded`) 중
> `b` 다 — [`../README.md`](../README.md) 참고. 아래 내용은 2→3단계로 넘어갈 때 생기는
> 변화(메인/워커 분리, 백그라운드 위임)를 그대로 설명하고, `b` 고유의 문제(승인 카드가
> 통째로 몰려서 뜨는 것)는 다루지 않는다 — 그건 `../README.md` 에 있다.

## 안 바뀌는 것

`../servers/` 전부 · `static/style.css` · `mcp_config()` · `make_checkpointer()` · `LOOP`/`run()`

## app.py — 핵심 변경 한 줄

2단계의 `drive()` 가 `run_job()` 이 된다. **루프 뼈대는 그대로고 한 갈래만 바뀐다.**

```python
# 2단계 drive()                    # 3단계 run_job()
while True:                        while True:
    calls = ...                        calls = ...
    if not calls: return done          if not calls: 작업 완료; return
    risky = [...]                      risky = [...]
    if risky:                          if risky:
        return pending  ◀────바뀌는 곳────▶  await job["_event"].wait()
    state = await ainvoke(None)        state = await ainvoke(None)
```

**응답하고 빠진다 → 잠들어서 기다린다.**
웹 요청은 기다릴 수 없지만 백그라운드 워커는 기다릴 수 있다. 이 차이가 3단계 전부다.

## app.py — 에이전트 2개로 분리

| | 도구 | 정지 |
|---|---|---|
| **메인** (대화) | 조회 도구 + `delegate_task` · `list_jobs` | 없음 — 대화가 끊기면 안 되니까 |
| **워커** (실행) | MCP 도구 전부 | `interrupt_before=["tools"]` |

`SYSTEM` 하나가 `MAIN_SYSTEM` / `WORKER_SYSTEM` 둘로 나뉜다.

> 메인에는 계정을 바꾸는 도구를 **아예 안 준다.** "직접 하지 마"라고 프롬프트로 부탁하는 것보다
> 손에 안 쥐어주는 게 확실하다.

## app.py — 추가

| 추가 | 하는 일 |
|---|---|
| `JOBS` · `new_job()` | 작업 저장소 (id / 상태 / 로그 / 승인대기) |
| `spawn()` | 결과를 안 기다리고 루프에 던져둔다 (`run()` 과 짝) |
| `delegate_task` | 로컬 `@tool`. 작업 만들고 **즉시** 번호만 반환 → 채팅이 안 막힌다 |
| `asyncio.Event` | 워커를 재우고 깨우는 신호. 스레드를 안 붙잡아서 그 사이 채팅이 돈다 |

## app.py — 엔드포인트

```
/approve  (2단계)   →   /jobs              작업 목록 (1초 폴링)
                        /jobs/<id>/decide  승인·거부 → Event.set()
```

`app.run(..., threaded=True)` 로 바꾼다 — 폴링과 채팅이 동시에 들어온다.

## index.html — 레이아웃 변경

- 1단 → **2단 그리드**(`.layout`): 왼쪽 채팅 / 오른쪽 작업 패널
- 승인 카드가 채팅창이 아니라 **작업 패널** 안으로 이동
- `setInterval(pollJobs, 1000)` — 워커가 승인 대기에 들어가면 폴링이 발견해 카드를 그린다

## 핵심 한 줄

`thread_id` 가 작업마다 다르다 = 완전히 분리된 대화. 그래서 **여러 작업이 동시에 진행되고
각자 따로 승인을 기다린다.**
