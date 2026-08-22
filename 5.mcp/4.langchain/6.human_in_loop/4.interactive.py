"""
4.interactive.py — 대화형 비서 (사람이 계속 질문하고, 위험한 작업만 승인한다).

1~3 은 질문이 코드에 하드코딩된 '한 방 실행' 데모였다.
여기서는 터미널에서 직접 질문을 입력하며 대화를 이어간다 — 실제 앱에 가장 가까운 형태다.

1~3 에 없던 것 두 가지:

  (1) 멀티턴 대화 — 같은 thread_id 를 계속 쓰므로 이전 대화를 기억한다.
      "report.txt 읽어줘" → "그거 지워줘" 처럼 '그거' 가 통한다.
      (checkpointer 가 대화 이력을 thread_id 별로 보관한다)

  (2) 승인이 흐름에 자연스럽게 섞인다 — 조회는 그냥 되고, 삭제/발송에서만 멈춘다.
      HITL 이 '데모용 장치' 가 아니라 앱의 일부로 어떻게 사는지 보인다.

── 해볼 만한 대화 ──────────────────────────────────────────────
    문서함에 뭐 있어?                    ← 조회, 안 물어봄
    report.txt 내용 보여줘               ← 조회, 안 물어봄
    그 내용을 boss@example.com 에게 메일로 보내줘   ← ⚠️ 승인 질문 (그리고 '그 내용' 이 통한다)
    old_backup.zip 지워줘                ← ⚠️ 승인 질문. n 을 눌러 거부해 보기
    방금 왜 안 지웠지?                    ← 거부한 맥락을 기억하고 답한다

실행:
  python 4.interactive.py          ← server.py 는 stdio 로 자동 실행
  종료: quit / exit / 종료  또는 Ctrl+C
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")

# 되돌릴 수 없거나 외부로 나가는 도구만 승인 대상
RISKY_TOOLS = {"delete_file", "send_email"}
EXIT_WORDS = {"quit", "exit", "종료", "q"}

SYSTEM_PROMPT = """너는 문서함을 관리하는 비서다.
도구로 조회한 사실만 근거로 답하고 추측하지 않는다.
사용자가 어떤 작업을 거부하면 존중하고, 억지로 다시 시도하지 않는다.
답변은 한국어로 간결하게 한다."""


def ask_approval(call) -> bool:
    """위험한 도구 호출을 보여주고 승인 여부를 받는다."""
    print(f"\n  ⚠️  승인 필요: {call['name']}")
    for key, value in call["args"].items():
        text = str(value)
        if len(text) > 100:                        # 메일 본문처럼 긴 인자는 잘라서 보여준다
            text = text[:100] + " …"
        print(f"        {key} = {text}")
    return input("      실행할까요? (y/n): ").strip().lower() == "y"


async def run_turn(agent, config, question: str) -> str:
    """질문 하나를 처리한다. 도구 호출 때마다 필요하면 승인을 받고, 최종 답변을 돌려준다."""
    result = await agent.ainvoke({"messages": [("user", question)]}, config=config)
    shown = len(result["messages"])      # 어디까지 화면에 찍었는지 (messages 는 append-only)

    while result["messages"][-1].tool_calls:
        calls = result["messages"][-1].tool_calls
        for c in calls:
            if c["name"] not in RISKY_TOOLS:
                print(f"  → {c['name']}({c['args']})")

        rejected = {c["id"] for c in calls if c["name"] in RISKY_TOOLS and not ask_approval(c)}

        if rejected:
            # 거부 — tools 노드를 건너뛰고 거부 사실을 결과로 주입한다 (2.risky_only 와 같은 기법).
            #   as_node="tools" 가 없으면 도구가 그대로 실행돼 버린다.
            #   tool_call 하나당 ToolMessage 하나 — id 를 맞춰야 한다.
            agent.update_state(
                config,
                {"messages": [
                    ToolMessage(
                        content="사용자가 이 작업을 거부했습니다. 실행하지 않았습니다.",
                        tool_call_id=c["id"],
                        name=c["name"],
                    )
                    for c in calls
                ]},
                as_node="tools",
            )
            print("      ✗ 거부됨")

        result = await agent.ainvoke(None, config=config)

        # 실행된 도구의 결과를 보여준다 (재개 직후 messages[-1] 은 이미 다음 AIMessage 라
        # ToolMessage 가 그 앞에 묻힌다 → 새로 생긴 메시지를 훑어야 보인다)
        for m in result["messages"][shown:]:
            if m.type == "tool":
                head = str(m.content).replace("\n", " / ")
                print(f"  ← {m.name}: {head[:160]}")
        shown = len(result["messages"])

    return result["messages"][-1].content or "(최종 답변 없음)"


async def main():
    client = MultiServerMCPClient({
        "docs": {"command": "python", "args": [SERVER], "transport": "stdio"},
    })
    tools = await client.get_tools()

    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
        interrupt_before=["tools"],
    )
    # 대화 내내 같은 thread_id → 이전 턴을 기억한다 ('그거 지워줘' 가 통하는 이유)
    config = {"configurable": {"thread_id": "chat-session"}}

    print("=" * 60)
    print("문서함 비서 — 무엇이든 물어보세요")
    print(f"  자동 통과: {[t.name for t in tools if t.name not in RISKY_TOOLS]}")
    print(f"  승인 필요: {sorted(RISKY_TOOLS)}")
    print("  종료: quit / exit / 종료")
    print("=" * 60)

    while True:
        try:
            question = input("\n[나] ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not question:
            continue
        if question.lower() in EXIT_WORDS:
            print("종료합니다.")
            break

        try:
            answer = await run_turn(agent, config, question)
        except Exception as e:
            print(f"\n[오류] {type(e).__name__}: {e}")
            continue

        print(f"\n[비서] {answer}")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - HITL 은 데모용 장치가 아니라 앱의 상시 구성요소다. 조회는 흐르고 위험한 것만 멈춘다.
#   - thread_id 를 고정해 대화 이력을 유지하는 게 '그거/방금' 같은 지시어가 통하는 이유다.
#   - MemorySaver 는 프로세스가 죽으면 이력도 사라진다. 실제 앱은 SqliteSaver/PostgresSaver 를 쓰고,
#     thread_id 를 사용자/세션 단위로 발급한다 (같은 코드로 여러 사용자 대화가 분리된다).
