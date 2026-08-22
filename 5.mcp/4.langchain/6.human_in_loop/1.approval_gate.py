"""
1.approval_gate.py — MCP 도구를 부르기 전에 사람에게 승인받는다 (가장 단순한 형태).

이 예제: 에이전트가 MCP 도구를 호출하려 할 때마다 멈춰서 y/n 을 묻고, y 일 때만 실행한다.

── 왜 클라이언트에서 막는가 ────────────────────────────────────
  MCP 도구는 '남이 만든 서버' 의 도구다. 서버 코드를 내가 고칠 수 없다.
  server.py 의 delete_file 에는 확인 절차가 전혀 없다 — 부르면 그냥 지운다.
  그러니 안전장치를 걸 수 있는 유일한 지점이 클라이언트다.
  Claude Desktop / Claude Code 가 도구 호출마다 승인창을 띄우는 게 정확히 이 구조다.

  (서버가 스스로 되묻는 방식 = MCP elicitation → 1.basic/4.advanced/3.elicitation.
   그건 서버 저자가 ctx.elicit() 을 넣어줬을 때만 가능하다.)

── 동작 원리 ───────────────────────────────────────────────────
  MCP 도구도 변환되고 나면 그냥 LangChain BaseTool 이다.
  → 2.langchain/8.agents/6.hitl_streaming 에서 로컬 @tool 에 쓰던
    interrupt_before=["tools"] 가 MCP 도구에도 그대로 통한다. 특별한 코드가 없다.

  agent.ainvoke()              → 도구 호출 직전 정지
  input() 으로 y/n             → 사람 판단
  agent.ainvoke(None, config)  → 정지 지점부터 재개 (도구 실행)

준비:
  pip install mcp langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
  .env 에 OPENAI_API_KEY

실행:
  python 1.approval_gate.py        ← server.py 는 stdio 로 자동 실행된다
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
SERVER = os.path.join(HERE, "server.py")


async def main():
    # ─── MCP 서버 연결 → 도구 가져오기 ─────────────────────────
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
    # thread_id — 이 대화의 이름표. 재개할 때 같은 값이어야 정지 지점부터 이어진다.
    config = {"configurable": {"thread_id": "approval-demo"}}

    question = "문서함에 어떤 파일이 있는지 보고, old_backup.zip 을 삭제해줘."
    print("=" * 60)
    print(f"[user] {question}")
    print("=" * 60)

    result = await agent.ainvoke({"messages": [("user", question)]}, config=config)

    # 어디까지 화면에 찍었는지 표시해 두는 커서.
    #   messages 는 뒤에만 붙으므로(append-only) 인덱스 하나로 '새로 생긴 것' 을 구분할 수 있다.
    shown = len(result["messages"])

    rejected = False

    # ─── 도구를 부르려 할 때마다 반복해서 승인받는다 ───────────
    #   이 질문은 list_files → delete_file 로 두 번 멈춘다.
    #   마지막 메시지에 tool_calls 가 없으면 = 최종 답변 도달 → 루프 종료.
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

        # ─── 실행된 도구의 '결과' 를 보여준다 ──────────────────
        #   이걸 찍지 않으면 y 를 눌러도 화면에 아무 반응이 없어 보인다.
        #   재개하자마자 LLM 이 다음 도구를 제안하므로 messages[-1] 은 이미 다음 AIMessage 다.
        #   도구 결과(ToolMessage)는 그 앞에 묻혀 있어서, 새로 생긴 메시지를 훑어야 보인다.
        for m in result["messages"][shown:]:
            if m.type == "tool":
                print(f"  ← {m.name} 결과: {m.content}")
        shown = len(result["messages"])

    # 거부로 빠져나왔다면 위에서 이미 [중단] 을 찍었으므로 최종 답변은 없다
    if not rejected:
        print(f"\n[ai] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - MCP 도구든 로컬 @tool 이든 승인 코드는 완전히 같다 (둘 다 BaseTool).
#   - 단점: 조회처럼 안전한 도구까지 전부 묻는다 → 금방 피곤해진다.
#     실무에선 '위험한 것만' 묻는다 → 2.risky_only.py
