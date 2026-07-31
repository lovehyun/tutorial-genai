"""
3.plan_approve.py — 도구 하나하나가 아니라 '작업 계획 전체' 를 먼저 승인받는다.

1·2 와 승인의 '단위' 가 다르다:

    1.approval_gate / 2.risky_only : 도구 호출 직전마다 묻는다 (실행 중 승인)
    3.plan_approve                 : 시작 전에 계획을 통째로 보여주고 한 번 묻는다 (실행 전 승인)

  전자는 매 단계 통제할 수 있지만 질문이 잦다(승인 피로).
  후자는 딱 한 번만 묻지만, 승인한 뒤로는 중간에 못 멈춘다.
  → 되돌릴 수 있는 작업을 여러 번 하는 흐름에 어울린다. 둘을 섞어 쓰기도 한다(아래 메모).

── 핵심 트릭: 계획 단계에서는 도구를 아예 주지 않는다 ──────────
  "계획만 세우고 실행하지 마" 라고 프롬프트로 부탁하면 LLM 이 종종 어긴다.
  도구를 바인딩하지 않은 순수 LLM 에게 도구 '목록' 만 텍스트로 보여주면
  실행하고 싶어도 실행할 수단이 없다. 프롬프트 부탁보다 구조가 확실하다.

  1단계: 도구 없는 LLM   + 도구 설명 텍스트  → 계획 작성
  2단계: 사람 승인
  3단계: 도구 있는 에이전트 + 승인된 계획    → 실행 (중간에 안 묻는다)

실행:
  python 3.plan_approve.py         ← server.py 는 stdio 로 자동 실행
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")

PLANNER_PROMPT = """너는 작업 계획을 세우는 역할이다. 실행은 다른 담당자가 한다.

사용 가능한 도구:
{tool_list}

사용자 요청을 처리하기 위해 어떤 도구를 어떤 순서로 부를지 번호 매긴 계획으로만 답하라.
  - 각 줄 형식: `N. 도구이름(인자=값) — 왜 필요한지 한 줄`
  - 되돌릴 수 없는 작업(삭제, 발송)에는 줄 앞에 ⚠️ 를 붙인다.
  - 계획 외의 인사말이나 설명은 쓰지 않는다."""

EXECUTOR_PROMPT = """너는 승인된 계획을 실행하는 담당자다.

승인된 계획:
{plan}

이 계획에 있는 작업만 수행한다. 계획에 없는 도구는 부르지 않는다.
계획대로 진행할 수 없는 상황(파일이 없는 등)을 만나면 임의로 다른 작업을 하지 말고
무엇이 막혔는지 보고하고 멈춘다.
작업이 끝나면 무엇을 했는지 한국어로 간결하게 정리한다."""


async def main():
    client = MultiServerMCPClient({
        "docs": {"command": "python", "args": [SERVER], "transport": "stdio"},
    })
    tools = await client.get_tools()

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    question = "old_backup.zip 을 지우고, 남은 파일 목록을 boss@example.com 으로 메일 보내줘."
    print("=" * 60)
    print(f"[user] {question}")
    print("=" * 60)

    # ─── 1단계: 계획 수립 (도구를 붙이지 않은 LLM) ─────────────
    #   tools 를 bind 하지 않았으므로 이 LLM 은 도구를 부를 수단 자체가 없다.
    tool_list = "\n".join(f"- {t.name}: {t.description}" for t in tools)
    planner_messages = [
        ("system", PLANNER_PROMPT.format(tool_list=tool_list)),
        ("user", question),
    ]
    plan = (await llm.ainvoke(planner_messages)).content

    print("\n[에이전트가 세운 계획]")
    print(plan)

    # ─── 2단계: 계획 전체를 한 번만 승인받는다 ─────────────────
    approval = input("\n이 계획대로 진행할까요? (y/n): ").strip().lower()
    if approval != "y":
        print("\n[중단] 계획이 승인되지 않아 아무 것도 실행하지 않았습니다.")
        return

    # ─── 3단계: 승인된 계획을 실행 (중간에 묻지 않는다) ────────
    #   checkpointer 도 interrupt_before 도 없다 — 멈출 일이 없기 때문.
    executor = create_agent(llm, tools, system_prompt=EXECUTOR_PROMPT.format(plan=plan))
    result = await executor.ainvoke({"messages": [("user", question)]})

    print("\n[실행 내역]")
    for m in result["messages"]:
        if getattr(m, "tool_calls", None):
            for c in m.tool_calls:
                print(f"  → {c['name']}({c['args']})")
        if m.type == "tool":                       # 도구가 실제로 돌려준 결과
            head = str(m.content).replace("\n", " / ")
            print(f"  ← {m.name}: {head[:200]}")

    print(f"\n[ai] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# ── 트레이드오프 정리 ───────────────────────────────────────────
#   장점: 질문이 딱 한 번. 사람이 '전체 그림' 을 보고 판단한다
#         (도구 단위 승인은 나무만 보여서, 정작 전체 방향이 틀린 걸 놓치기 쉽다).
#   단점: 계획 시점에 모르는 정보가 있으면 계획이 어긋난다.
#         예) "파일 목록 보고 오래된 것 삭제" → 목록을 봐야 뭘 지울지 정해진다.
#         승인 후에는 멈출 수 없으므로, 계획이 어긋나도 그대로 진행될 위험이 있다.
#
#   실무 조합: 계획을 승인받고(여기) + 되돌릴 수 없는 도구에서만 한 번 더 확인(2.risky_only).
#             executor 를 create_agent(..., checkpointer=..., interrupt_before=["tools"]) 로 만들고
#             2.risky_only 의 while 루프를 그대로 붙이면 된다.
