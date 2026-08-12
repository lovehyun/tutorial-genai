"""
4b 확장 — "항상 허용"이라고 한 번 답하면, 그 도구는 이후로 다시 안 묻는다(허용 리스트에 추가).
18.mcp_ops_assistant/4.auto_approve 의 AUTO_APPROVED 집합 아이디어를 CLI로 단순화한 것.

레포에 CLI 형태의 자동승인 예제는 없다 — 4b(interrupt_before 승인 루프)를 그대로 확장해서
이번 세션에서 직접 구성. 4a.hitl_approval_server.py 를 그대로 재사용한다.

시나리오: "old_backup.zip 삭제해줘" → 승인 프롬프트에서 a(항상 허용) 선택
        → "report.txt 도 삭제해줘"(별도 턴) → 같은 도구(delete_file)라 안 물어보고 바로 실행되는지 확인.

실행: python 4cx.hitl_auto_approve.py   (첫 프롬프트에서 a 를 입력해보자)
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "4a.hitl_approval_server.py")

AUTO_APPROVED = set()  # 한 번 "항상 허용" 하면 도구 이름이 여기 쌓인다 — 4.auto_approve와 같은 아이디어


async def run_turn(agent, config, message: str, shown: int) -> int:
    """사용자 메시지 하나를 처리한다. 필요하면 승인/자동승인 루프를 돌고,
    다음 턴에서 이어 쓸 수 있게 '지금까지 보여준 메시지 개수'를 반환한다."""
    print(f"\n[user] {message}")
    result = await agent.ainvoke({"messages": [("user", message)]}, config=config)

    while result["messages"][-1].tool_calls:
        calls = result["messages"][-1].tool_calls

        if all(c["name"] in AUTO_APPROVED for c in calls):
            # 도구 "이름"만 기억한다 — 이번엔 delete_file(report.txt)인데,
            # 아까 delete_file(old_backup.zip)을 항상 허용해서 인자가 달라도 그냥 통과된다.
            print("\n[자동승인] 이전에 '항상 허용'한 도구라 묻지 않고 진행:")
            for c in calls:
                print(f"  ⚡ {c['name']}({c['args']})")
        else:
            print("\n[정지 — 실행 예정]")
            for c in calls:
                print(f"  → {c['name']}({c['args']})")

            approval = input("\n실행할까요? (y=한 번만 / a=항상 허용 / n=거부): ").strip().lower()

            if approval == "a":
                for c in calls:
                    AUTO_APPROVED.add(c["name"])
                print(f"  ⚡ '{', '.join(c['name'] for c in calls)}' 를 항상 허용 목록에 추가했습니다.")
            elif approval != "y":
                print("\n[중단] 사용자가 거부하여 실행하지 않았습니다.")
                return len(result["messages"])

        result = await agent.ainvoke(None, config=config)

        for m in result["messages"][shown:]:
            if m.type == "tool":
                print(f"  ← {m.name} 결과: {m.content}")
        shown = len(result["messages"])

    print(f"[ai] {result['messages'][-1].content}")
    return len(result["messages"])


async def main():
    client = MultiServerMCPClient({
        "docs": {"command": "python", "args": [SERVER], "transport": "stdio"},
    })
    tools = await client.get_tools()
    print(f"MCP 도구 {len(tools)}개:", [t.name for t in tools])

    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        checkpointer=MemorySaver(),
        interrupt_before=["tools"],
    )
    config = {"configurable": {"thread_id": "auto-approve-demo"}}

    print("=" * 60)
    shown = await run_turn(agent, config, "old_backup.zip 삭제해줘. (승인 프롬프트에서 a 를 입력해보자)", 0)

    print("\n" + "=" * 60)
    shown = await run_turn(agent, config, "report.txt 도 삭제해줘.", shown)


if __name__ == "__main__":
    asyncio.run(main())


# ─── 실행 결과 (2026-08-12, gpt-4o-mini, 첫 프롬프트에 'a' 입력) ─
# [user] old_backup.zip 삭제해줘. (승인 프롬프트에서 a 를 입력해보자)
# [정지 — 실행 예정]
#   → delete_file({'name': 'old_backup.zip'})
#   ⚡ 'delete_file' 를 항상 허용 목록에 추가했습니다.
#   ← delete_file 결과: 'old_backup.zip' 삭제 완료.
# [ai] old_backup.zip 파일이 삭제되었습니다.
#
# [user] report.txt 도 삭제해줘.
# [자동승인] 이전에 '항상 허용'한 도구라 묻지 않고 진행:
#   ⚡ delete_file({'name': 'report.txt'})
#   ← delete_file 결과: 'report.txt' 삭제 완료.
# [ai] report.txt 파일이 삭제되었습니다.
#   → 두 번째 삭제는 프롬프트 없이 바로 실행됐다 — 자동승인이 실제로 동작한다.


# 관전 포인트: AUTO_APPROVED 는 "도구 이름" 단위다. delete_file 을 한 번 항상 허용하면
# 인자(어떤 파일인지)와 무관하게 delete_file 호출이면 뭐든 통과된다 — 18.mcp_ops_assistant의
# README가 짚었던 바로 그 한계("자동승인 범위가 너무 넓다")를 CLI로도 그대로 재현한 것.
#
# ⚠️ 별개의 관찰: 실행해보면 두 번째 삭제 후에도 "남은 파일 2개"로 찍힌다(1개가 맞을 것 같은데).
#   MultiServerMCPClient 로 얻은 도구는 호출마다(또는 턴마다) 서버를 새로 붙이는 식이라,
#   server.py 의 메모리 속 DOCS 상태가 턴 사이에 안 이어지는 것으로 보인다 — 자동승인 로직과는
#   무관한 별개의 현상이다(4b 원본도 같은 구조라 같은 한계를 갖는다). 실제 운영에선 DB처럼
#   프로세스 밖에 상태를 두면 해결된다(18.mcp_ops_assistant가 ops.db 파일을 쓰는 이유이기도 하다).
