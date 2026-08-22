"""
2.risky_only.py — 위험한 도구만 승인받고, 거부하면 에이전트가 대안을 찾게 한다.

1.approval_gate.py 에서 두 가지가 달라진다:

  (1) 선별 승인 — 조회(list_files/read_file)는 묻지 않고 자동 통과,
      되돌릴 수 없는 작업(delete_file/send_email)만 사람에게 묻는다.
      전부 물으면 사용자가 지쳐서 결국 아무거나 y 를 누른다(승인 피로).

  (2) 거부가 '중단' 이 아니라 '대화' 다 — 거부하면 그 사실을 도구 결과로 만들어
      에이전트에게 돌려준다. 에이전트는 그걸 읽고 다른 방법을 제안하거나 이유를 묻는다.
      1.approval_gate 처럼 그냥 return 해버리면 에이전트는 왜 멈췄는지도 모른다.

── 거부를 어떻게 에이전트에게 알리나 (핵심 기법) ────────────────
  그냥 재개하면(ainvoke(None)) 도구가 실행돼 버린다. 실행을 건너뛰려면
  "tools 노드가 이미 실행된 것처럼" 상태를 덮어써야 한다:

      agent.update_state(config, {"messages": [거부 ToolMessage]}, as_node="tools")
                                                                   ^^^^^^^^^^^^^^^
  as_node="tools" 가 없으면 → 상태에 메시지만 추가되고 tools 노드는 여전히 실행된다.
  있으면 → tools 노드를 건너뛰고 바로 LLM 으로 넘어간다.

  ※ tool_call_id 를 반드시 맞춰야 한다. OpenAI 는 tool_call 하나당 결과 하나를
    요구하므로, 짝이 안 맞으면 다음 호출에서 에러가 난다.

실행:
  python 2.risky_only.py           ← server.py 는 stdio 로 자동 실행
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

# ─── 승인이 필요한 도구 (되돌릴 수 없거나 외부로 나가는 것) ─────
#   화이트리스트가 아니라 블랙리스트인 이유: 서버에 새 도구가 추가됐을 때
#   '모르는 도구' 가 자동 통과되면 안 되기 때문... 은 사실 반대다.
#   실무에선 '아는 안전한 도구만 통과' 시키는 화이트리스트가 더 안전하다.
#   여기선 도구가 4개뿐이라 읽기 쉬운 쪽을 택했다 (SAFE 방식은 아래 주석 참고).
RISKY_TOOLS = {"delete_file", "send_email"}

SYSTEM_PROMPT = """너는 문서함을 관리하는 비서다.
도구로 조회한 사실만 근거로 답하고, 추측하지 않는다.
사용자가 어떤 작업을 거부하면 그 이유를 존중하고, 억지로 다시 시도하지 말고
대신 할 수 있는 다른 방법을 한 가지 제안한다.
답변은 한국어로 간결하게 한다."""


def ask_approval(call) -> bool:
    """위험한 도구 호출 하나를 사람에게 보여주고 승인 여부를 받는다."""
    print(f"\n  ⚠️  승인 필요: {call['name']}")
    for key, value in call["args"].items():
        print(f"        {key} = {value}")
    return input("      실행할까요? (y/n): ").strip().lower() == "y"


async def main():
    client = MultiServerMCPClient({
        "docs": {"command": "python", "args": [SERVER], "transport": "stdio"},
    })
    tools = await client.get_tools()

    safe = [t.name for t in tools if t.name not in RISKY_TOOLS]
    print(f"자동 통과 도구: {safe}")
    print(f"승인 필요 도구: {sorted(RISKY_TOOLS)}\n")

    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
        interrupt_before=["tools"],
    )
    config = {"configurable": {"thread_id": "risky-only"}}

    question = "old_backup.zip 을 삭제하고, 정리 결과를 boss@example.com 으로 메일 보내줘."
    print("=" * 60)
    print(f"[user] {question}")
    print("=" * 60)

    result = await agent.ainvoke({"messages": [("user", question)]}, config=config)
    shown = len(result["messages"])      # 어디까지 화면에 찍었는지 (messages 는 append-only)

    while result["messages"][-1].tool_calls:
        calls = result["messages"][-1].tool_calls

        # ─── 이번에 부르려는 도구들을 훑어 거부된 것을 모은다 ───
        rejected = {}
        for call in calls:
            if call["name"] in RISKY_TOOLS:
                if not ask_approval(call):
                    rejected[call["id"]] = call["name"]
            else:
                print(f"\n  ✓ 자동 통과: {call['name']}({call['args']})")

        if rejected:
            # ─── 거부됨: tools 노드를 건너뛰고 거부 사실을 결과로 주입 ───
            #   같은 배치의 도구는 전부 실행하지 않는다 (일부만 실행하면 상태가 어중간해진다).
            #   tool_call 하나당 ToolMessage 하나 — id 를 반드시 맞춘다.
            messages = [
                ToolMessage(
                    content=("사용자가 이 작업을 거부했습니다. 실행하지 않았습니다."
                             if call["id"] in rejected else
                             "같은 요청의 다른 작업이 거부되어 함께 취소되었습니다."),
                    tool_call_id=call["id"],
                    name=call["name"],
                )
                for call in calls
            ]
            agent.update_state(config, {"messages": messages}, as_node="tools")
            print("\n  ✗ 거부 — 에이전트에게 알리고 대안을 물어봅니다.")
        else:
            print("\n  → 실행합니다.")

        # 승인이든 거부든 재개는 똑같다.
        #   승인 → tools 노드 실행 / 거부 → 위에서 이미 건너뛴 상태로 LLM 이 이어받음
        result = await agent.ainvoke(None, config=config)

        # ─── 도구 결과 표시 ────────────────────────────────────
        #   재개하면 LLM 이 곧바로 다음 도구를 제안하므로 messages[-1] 은 이미 다음 AIMessage 다.
        #   도구 결과(ToolMessage)는 그 앞에 묻혀 있어서, 새로 생긴 메시지를 훑어야 보인다.
        for m in result["messages"][shown:]:
            if m.type == "tool":
                head = str(m.content).replace("\n", " / ")
                print(f"      ← {m.name}: {head[:200]}")
        shown = len(result["messages"])

    final = result["messages"][-1].content
    print(f"\n[ai] {final}" if final else "\n[ai] (최종 답변 없이 종료)")


if __name__ == "__main__":
    asyncio.run(main())


# ── 실무 적용 메모 ──────────────────────────────────────────────
#   - 화이트리스트가 더 안전하다: RISKY_TOOLS 블랙리스트 대신
#         SAFE_TOOLS = {"list_files", "read_file"}
#         if call["name"] not in SAFE_TOOLS:  ask_approval(call)
#     로 뒤집으면, 서버에 새 도구가 추가돼도 '모르는 도구' 는 자동 통과되지 않는다.
#     외부 MCP 서버는 내가 모르는 사이에 도구가 늘 수 있으므로 이쪽이 원칙이다.
#   - 인자까지 고쳐서 승인하고 싶다면 update_state 로 AIMessage 의 tool_calls 를 덮어쓴다
#     → 2.langchain/8.agents/6.hitl_streaming/6.5_ask_or_edit.py 참고.
#   - 터미널 input() 대신 웹/슬랙 승인으로 바꿔도 구조는 같다. 정지 상태가 checkpointer 에
#     남아 있으므로, 프로세스가 죽었다 살아나도 같은 thread_id 로 재개할 수 있다
#     (MemorySaver 는 메모리라 재시작하면 사라진다 → 실무에선 SqliteSaver/PostgresSaver).
