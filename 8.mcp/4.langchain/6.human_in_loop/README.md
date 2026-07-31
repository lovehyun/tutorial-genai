# 4.langchain/6.human_in_loop — MCP 도구 + 사람 승인(HITL)

에이전트가 **되돌릴 수 없는 일**(삭제·송금·메일 발송·DB 수정)을 하려 할 때
실행 직전에 멈춰 사람에게 확인받는다.

## 왜 클라이언트에서 막나

MCP 도구는 **남이 만든 서버**의 도구다. 이 폴더의 [server.py](server.py)를 보면
`delete_file` 에 확인 절차가 **전혀 없다** — 부르면 그냥 지운다. 그게 정상적인 MCP 서버다.
서버 코드를 내가 고칠 수 없으니, 안전장치를 걸 수 있는 유일한 지점은 **클라이언트**다.

> Claude Desktop / Claude Code가 도구 호출마다 승인창을 띄우는 게 정확히 이 구조다.

## 레포의 다른 HITL 방식과의 관계

| 방식 | 누가 묻나 | 위치 | 한계 |
|---|---|---|---|
| **MCP elicitation** | **서버**가 묻는다 (`ctx.elicit()`) | [1.basic/4.advanced/3.elicitation](../../1.basic/4.advanced/3.elicitation/) | 서버 저자가 넣어줘야만 동작 |
| **클라이언트 승인 게이트** | **클라이언트**가 막는다 | **여기** | 서버 협조 불필요 — 어떤 서버에도 적용 |
| 로컬 도구 승인/인자수정 | 클라이언트 | [2.langchain/8.agents/6.hitl_streaming](../../../2.langchain/8.agents/6.hitl_streaming/) | MCP 아닌 로컬 `@tool` 대상 |
| `human` 도구 (되묻기) | 에이전트가 사람에게 질문 | [1.9_human.py](../../../2.langchain/8.agents/1.builtin_tools/1.9_human.py) | 승인이 아니라 **정보 수집** |

핵심은 **elicitation ↔ 승인 게이트**의 대비다. 전자는 서버가 협조할 때, 후자는 협조를 기대할 수 없을 때.

## 파일

| 파일 | 무엇을 | 승인 단위 |
|---|---|---|
| `server.py` | 안전한 도구(`list_files`, `read_file`) + 위험한 도구(`delete_file`, `send_email`). **아무 것도 막지 않는다** | — |
| `1.approval_gate.py` | 모든 도구 호출 전 y/n — 가장 단순한 형태 | 도구마다 |
| `2.risky_only.py` | 위험한 도구만 승인 + **거부하면 에이전트가 대안을 제안** | 위험한 도구만 |
| `3.plan_approve.py` | **작업 계획 전체를 먼저 보여주고 한 번만 승인** | 작업 단위 |
| `4.interactive.py` | **대화형 비서** — 직접 질문하며 대화, 위험한 작업만 승인 | 위험한 도구만 |

데이터는 전부 메모리 안의 가짜다. 실제 파일이 지워지거나 메일이 나가지 않는다.

### 승인 단위 — 언제 무엇을 쓰나

```
1·2 (실행 중 승인)          3 (실행 전 승인)
  도구 → [승인?] → 실행       계획 전체 → [승인?] → 쭉 실행
  도구 → [승인?] → 실행
  도구 → [승인?] → 실행
  매 단계 통제 가능            질문 딱 한 번
  질문이 잦다(승인 피로)       승인 후엔 못 멈춘다
```

- **되돌릴 수 없는 작업이 섞여 있다** → `2.risky_only`
- **되돌릴 수 있는 작업을 여러 번 한다** → `3.plan_approve` (전체 방향을 사람이 먼저 검토)
- **실무 조합** — 계획을 승인받고(3) + 위험한 도구에서 한 번 더 확인(2). `3.plan_approve.py` 하단 메모 참고.

`3.plan_approve` 의 핵심 트릭: **계획 단계의 LLM 에는 도구를 아예 바인딩하지 않는다.**
"계획만 세우고 실행하지 마"라고 프롬프트로 부탁하면 LLM 이 종종 어기지만,
도구가 없으면 실행하고 싶어도 수단이 없다. 부탁보다 구조가 확실하다.

## 실행

```bash
cd 8.mcp/4.langchain/6.human_in_loop
pip install mcp langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
# .env 에 OPENAI_API_KEY

python 1.approval_gate.py
python 2.risky_only.py
python 3.plan_approve.py
python 4.interactive.py      # 대화형 — 직접 질문을 입력한다
```
> `server.py` 는 stdio 로 **자동 실행**된다. 터미널 하나면 된다.
> 실행하면 터미널이 `y/n` 을 물어보므로 직접 입력해야 진행된다.

`4.interactive.py` 에서 해볼 만한 대화 — 문맥이 이어지는지, 승인이 언제 뜨는지 확인:
```
문서함에 뭐 있어?                              ← 조회, 안 물어봄
report.txt 내용 보여줘                         ← 조회, 안 물어봄
그 내용을 boss@example.com 에게 메일로 보내줘   ← ⚠️ 승인 ('그 내용' 이 통한다)
old_backup.zip 지워줘                          ← ⚠️ 승인. n 을 눌러 거부해 보기
방금 왜 안 지웠지?                              ← 거부한 맥락을 기억하고 답한다
```

## 동작 원리 (3줄)

```python
agent = create_agent(llm, tools, checkpointer=MemorySaver(), interrupt_before=["tools"])
await agent.ainvoke({"messages": [...]}, config)   # → 도구 호출 직전 정지
await agent.ainvoke(None, config)                  # → 승인 후 그 지점부터 재개
```

- MCP 도구도 변환되고 나면 그냥 `BaseTool` 이라, 로컬 `@tool` 에 쓰던 코드가 **그대로** 통한다.
- `checkpointer` 가 있어야 정지 시점 상태가 저장돼 재개할 수 있다.
- 재개는 **같은 `thread_id`** 여야 한다.

## 관전 포인트

- **승인 피로** — `1.approval_gate` 는 조회까지 전부 묻는다. 사람이 지치면 결국 아무거나 `y` 를 누른다.
  그래서 `2.risky_only` 처럼 **되돌릴 수 없는 것만** 묻는 게 실무 형태다.
- **거부는 중단이 아니라 대화** — `2.risky_only` 는 거부 사실을 `ToolMessage` 로 만들어 에이전트에게 돌려준다.
  에이전트가 "그럼 대신 이렇게 할까요?" 로 이어간다. 그냥 종료하면 에이전트는 왜 멈췄는지도 모른다.
- **`as_node="tools"`** — 거부 시 도구 실행을 *건너뛰는* 핵심. 이게 없으면 메시지만 추가되고 도구는 그대로 실행된다.
- **`tool_call_id` 짝 맞추기** — OpenAI는 `tool_call` 하나당 결과 하나를 요구한다. 안 맞으면 다음 호출에서 에러.
- **도구 결과는 `messages[-1]` 에 없다** — 재개하면 도구가 실행되고 LLM이 **곧바로 다음 도구를 제안**하므로,
  마지막 메시지는 이미 다음 `AIMessage` 다. 도구 결과(`ToolMessage`)는 그 앞에 묻힌다.

  ```
  [... , ToolMessage(list_files 결과) , AIMessage(delete_file 호출)]
              ↑ 여기 있는데                        ↑ messages[-1]
  ```

  `messages[-1]` 만 찍으면 **`y` 를 눌러도 화면에 아무 반응이 없어 보인다.**
  `messages` 는 append-only 라서, 인덱스 커서(`shown`)로 새로 생긴 것만 훑으면 된다:

  ```python
  for m in result["messages"][shown:]:
      if m.type == "tool":
          print(f"  ← {m.name}: {m.content}")
  shown = len(result["messages"])
  ```

## 실무로 가져갈 때

- **화이트리스트가 원칙** — `RISKY_TOOLS` 블랙리스트보다 `SAFE_TOOLS` 화이트리스트가 안전하다.
  외부 MCP 서버는 내가 모르는 사이 도구가 늘 수 있고, 그때 '모르는 도구'가 자동 통과되면 안 된다.
- **`MemorySaver` 는 데모용** — 프로세스가 죽으면 정지 상태도 사라진다. 실제로는 `SqliteSaver` / `PostgresSaver`.
  영속 체크포인터를 쓰면 승인 UI를 터미널 대신 웹/슬랙으로 빼도 같은 구조로 동작한다.
- **프롬프트 가드레일과 병행** — 승인 게이트는 마지막 방어선이다. 애초에 위험한 도구를 덜 부르게 하는 건
  시스템 프롬프트 쪽 일이다 → [4.tools_safety](../4.tools_safety/).

## 추천 순서

`1.approval_gate`(가장 단순) → `2.risky_only`(선별 승인·거부 처리) → `3.plan_approve`(승인 단위 비교)
→ `4.interactive`(실제 앱 형태) → (서버가 직접 묻는 방식과 비교) [1.basic/4.advanced/3.elicitation](../../1.basic/4.advanced/3.elicitation/)
