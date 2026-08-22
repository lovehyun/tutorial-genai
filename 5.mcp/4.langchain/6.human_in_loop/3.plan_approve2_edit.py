"""
3.plan_approve2_edit.py — 3.plan_approve 에 '수정 요청' 을 더한 판.

3.plan_approve 는 y/n 뿐이라, 계획에서 틀린 데를 발견해도 취소밖에 못 한다.
그러면 처음부터 다시 말해야 한다. 사람이 '전체 그림' 을 보는 게 요점인데 절반이 죽는 셈이다.

    3.plan_approve       : y(실행) / n(취소)
    3.plan_approve2_edit : y(실행) / n(취소) / 그 외 아무 문장(수정 요청)

  "메일은 빼고 삭제만 해", "지우기 전에 목록 확인 단계를 넣어줘" 처럼
  고쳐가며 합의하는 게 실제 승인의 모습이다.

── 3.plan_approve 대비 바뀐 곳은 딱 한 군데 ────────────────────
  2단계의 승인 부분이 if 문에서 while 루프가 됐다. 나머지(1·3단계)는 완전히 동일하다.

      plan = LLM(planner_messages)          ┐
      사람이 y / n / 수정요청                │ 수정요청이면
      수정요청 → planner_messages 에 얹기 ──┘ 이 루프를 다시

  누적된 planner_messages 를 그대로 다시 넘기므로, LLM 은 앞서 낸 계획과 지적을
  모두 보고 다시 짠다. 대화 기록이 곧 수정 이력이다.

── 여전히 도구는 안 붙어 있다 ──────────────────────────────────
  계획 LLM 에 tools 를 bind 하지 않는다는 원본의 트릭이 여기서 배당을 낸다.
  실행할 수단 자체가 없으니, 계획을 몇 번을 고쳐 쓰든 실행될 위험이 0 이다.
  마음 놓고 반려할 수 있다.

실행:
  python 3.plan_approve2_edit.py         ← server.py 는 stdio 로 자동 실행

  수정 요청을 해볼 만한 문장:
    메일은 보내지 말고 삭제만 해
    지우기 전에 파일 목록부터 확인하는 단계를 넣어줘
    boss 말고 team@example.com 으로 보내
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

    # ─── 1단계: 계획 수립 준비 (3.plan_approve 와 동일) ────────
    tool_list = "\n".join(f"- {t.name}: {t.description}" for t in tools)
    planner_messages = [
        ("system", PLANNER_PROMPT.format(tool_list=tool_list)),
        ("user", question),
    ]

    # ─── 2단계: 승인 / 취소 / 수정요청 루프 ← 여기가 달라진 곳 ──
    round_no = 1
    while True:
        plan = (await llm.ainvoke(planner_messages)).content

        print(f"\n[계획 {round_no}차]")
        print(plan)

        answer = input(
            "\n진행하려면 y / 취소하려면 n / 고칠 점이 있으면 그대로 입력하세요\n> "
        ).strip()

        if answer.lower() in ("y", "yes", ""):
            break

        if answer.lower() in ("n", "no"):
            print("\n[중단] 계획이 승인되지 않아 아무 것도 실행하지 않았습니다.")
            return

        # y 도 n 도 아니면 = 수정 요청. 지적을 대화에 얹어 다시 짜게 한다.
        planner_messages.append(("assistant", plan))
        planner_messages.append(("user", f"다음 지적을 반영해 계획을 다시 작성하라: {answer}"))
        round_no += 1

    # ─── 3단계: 승인된 계획을 실행 (3.plan_approve 와 동일) ────
    #   넘기는 것은 '마지막으로 승인된' plan 이다 (수정 이력이 아니라 최종본).
    print(f"\n[승인됨 — {round_no}차 계획으로 실행합니다]")
    executor = create_agent(llm, tools, system_prompt=EXECUTOR_PROMPT.format(plan=plan))
    result = await executor.ainvoke({"messages": [("user", question)]})

    print("\n[실행 내역]")
    for m in result["messages"]:
        if getattr(m, "tool_calls", None):
            for c in m.tool_calls:
                print(f"  → {c['name']}({c['args']})")
        if m.type == "tool":
            head = str(m.content).replace("\n", " / ")
            print(f"  ← {m.name}: {head[:200]}")

    print(f"\n[ai] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# ── 더 해볼 것 (라이브 코딩용) ──────────────────────────────────
#   - 수정본은 계획 전체가 새로 나와서 뭐가 바뀌었는지 대조하기 어렵다.
#     difflib.ndiff 로 바뀐 줄만 뽑아 보여주면 읽기 쉬워진다 (LLM 을 더 부를 필요 없음).
#   - ⚠️ 는 LLM 이 붙이는 텍스트라 강제력이 없다. 빠뜨려도 코드가 잡아주지 않는다.
#     도구 목록에 [되돌릴 수 없음] 을 미리 박아 넘기면 LLM 이 '판단' 대신 '전달' 만 하게 된다.
#   - 근본적으로는 계획 승인만으로 부족하다 → 실무 조합은 3(계획 승인) + 2(위험 도구 재확인).
#     2.risky_only 의 RISKY_TOOLS 는 코드가 강제하므로 LLM 이 어길 수 없다.
