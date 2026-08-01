# 1단계 → 2단계 변경점

되돌릴 수 없는 작업 앞에서 멈추고 승인받는다.

## 안 바뀌는 것

`../servers/` 전부 · `static/style.css` · `mcp_config()` · 시스템 프롬프트 대부분

## app.py — 교체 3곳

**① 이벤트 루프** — 체크포인터가 요청을 넘어 살아 있어야 하므로, 요청마다 새 루프를 돌릴 수 없다.

```python
# 1단계                             # 2단계
asyncio.run(코루틴)                 LOOP = asyncio.new_event_loop()
                                    threading.Thread(target=LOOP.run_forever, daemon=True).start()
                                    def run(coro):
                                        return asyncio.run_coroutine_threadsafe(coro, LOOP).result()
```

**② 체크포인터** — 승인 대기가 브라우저·서버 재시작을 넘어 살아남아야 한다.

```python
checkpointer=MemorySaver()   →   checkpointer=await make_checkpointer()   # SQLite, 없으면 폴백
```

**③ 정지 옵션** — `create_agent(...)` 에 한 줄 추가.

```python
interrupt_before=["tools"]        # 도구 호출 직전마다 정지
```

## app.py — 추가

| 추가 | 하는 일 |
|---|---|
| `SAFE_TOOLS` | 조회 도구 화이트리스트 → 얘들만 안 묻고 통과 |
| `drive()` | 안전한 도구는 자동 실행, 위험한 도구를 만나면 `pending` 반환하고 **끝낸다**(안 기다림) |
| `resume()` | 승인 → 그냥 재개 / 거부 → `aupdate_state(..., as_node="tools")` 로 도구를 건너뛰고 거부 사실 주입 |
| `/approve` | 승인 버튼이 호출 → 멈춰 있던 에이전트를 꺼내 재개 |

> `as_node="tools"` 가 없으면 상태에 메시지만 얹히고 **도구는 그대로 실행된다.** 거부 처리의 핵심.

## index.html — 추가

- `renderApproval()` : 승인 카드 그리기 + 버튼 → `/approve`
- `handle()` : 서버 응답이 `done`(최종답변) 인지 `pending`(승인대기) 인지 분기

## 핵심 한 줄

CLI 의 `input()` 을 웹에서 흉내낼 수 없으니, **멈춘 에이전트를 저장소에 두고 승인 버튼이 꺼내 온다.**
기다림을 프로세스가 아니라 저장소가 담당한다.

## 이 단계의 한계 → 3단계로 가는 이유

승인 카드가 뜨면 **대화가 그 자리에서 멈춘다.** 승인할 때까지 다른 일을 못 한다.
