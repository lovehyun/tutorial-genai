"""
4b.hitl_approval_client.py — MCP 도구를 부르기 전에 사람에게 승인받는다 (가장 단순한 형태).
에이전트가 MCP 도구를 호출하려 할 때마다 멈춰서 y/n 을 묻고, y 일 때만 실행한다.

DONE — 2.student(todo) 의 agent 생성 TODO 를 채운 정답.

실행:
  python 4b.hitl_approval_client.py     ← 4a.hitl_approval_server.py 는 stdio 로 자동 실행된다
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

    # DONE: 도구 호출 직전에 멈추는 에이전트 완성
    #   힌트 1 — "정지 → 재개" 를 하려면 상태를 저장할 게 필요하다: checkpointer=MemorySaver() ← 채움
    #   힌트 2 — "tools" 노드(=도구 실행) 직전에 멈추게: interrupt_before=["tools"] ← 채움
    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        checkpointer=MemorySaver(),       # ← 채움
        interrupt_before=["tools"],       # ← 채움
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
