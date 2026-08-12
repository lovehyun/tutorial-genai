"""
4b.hitl_approval_client.py — MCP 도구를 부르기 전에 사람에게 승인받는다 (가장 단순한 형태).
에이전트가 MCP 도구를 호출하려 할 때마다 멈춰서 y/n 을 묻고, y 일 때만 실행한다.

핵심: MCP 도구도 변환되고 나면 그냥 LangChain BaseTool 이다.
      로컬 @tool 에 쓰던 interrupt_before=["tools"] 가 MCP 도구에도 그대로 통한다.

실행:
  python 4b.hitl_approval_client.py     ← 4a.hitl_approval_server.py 는 stdio 로 자동 실행된다

원본: 8.mcp/4.langchain/6.human_in_loop/1.approval_gate.py
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


async def main():
    client = MultiServerMCPClient({
        "docs": {
            "command": "python",
            "args": [SERVER],
            "transport": "stdio",
        },
    })
    tools = await client.get_tools()
    print(f"MCP 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    # ─── 승인 게이트: interrupt_before=["tools"] ───────────────
    #   checkpointer 가 있어야 '정지 → 재개' 가 가능하다 (정지 시점 상태를 저장해 둠).
    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        checkpointer=MemorySaver(),
        interrupt_before=["tools"],      # ← 도구 호출 직전 정지
    )
    config = {"configurable": {"thread_id": "approval-demo"}}

    question = "문서함에 어떤 파일이 있는지 보고, old_backup.zip 을 삭제해줘."
    print("=" * 60)
    print(f"[user] {question}")
    print("=" * 60)

    result = await agent.ainvoke({"messages": [("user", question)]}, config=config)
    shown = len(result["messages"])
    rejected = False

    while result["messages"][-1].tool_calls:
        print("\n[정지 — 실행 예정]")
        for call in result["messages"][-1].tool_calls:
            print(f"  → {call['name']}({call['args']})")

        approval = input("\n실행할까요? (y/n): ").strip().lower()

        if approval != "y":
            print("\n[중단] 사용자가 거부하여 실행하지 않았습니다.")
            rejected = True
            break

        result = await agent.ainvoke(None, config=config)       # 재개 → 도구 실행

        for m in result["messages"][shown:]:
            if m.type == "tool":
                print(f"  ← {m.name} 결과: {m.content}")
        shown = len(result["messages"])

    if not rejected:
        print(f"\n[ai] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# ─── 실행 결과 (2026-08-12, gpt-4o-mini, y/y 승인) ─────────────
# MCP 도구 4개: ['list_files', 'read_file', 'delete_file', 'send_email']
#
# [user] 문서함에 어떤 파일이 있는지 보고, old_backup.zip 을 삭제해줘.
#
# [정지 — 실행 예정]
#   → list_files({})
# 실행할까요? (y/n): y
#   ← list_files 결과: - report.txt / todo.md / old_backup.zip
#
# [정지 — 실행 예정]
#   → delete_file({'name': 'old_backup.zip'})
# 실행할까요? (y/n): y
#   ← delete_file 결과: 'old_backup.zip' 삭제 완료. 남은 파일 2개.
#
# [ai] 문서함에는 report.txt, todo.md 가 있습니다. old_backup.zip 은 삭제했습니다.
#
# (list_files 처럼 읽기 전용 도구까지 매번 묻는 게 이 방식의 한계 — 실무에선 '위험한 것만'
#  묻는 버전으로 발전시킨다. 원본 폴더의 2.risky_only.py 참고.)
