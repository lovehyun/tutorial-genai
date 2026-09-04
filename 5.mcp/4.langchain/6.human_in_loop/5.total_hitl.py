"""
5.total_hitl.py — 서버 3개(가짜 문서함 + 유틸/외부API + 진짜 파일시스템) 종합 HITL 데모.

1.approval_gate.py(전부 승인) · 2.risky_only.py(위험한 것만) 를 한 걸음 더 확장한다:
  - 서버가 하나가 아니라 **셋**이다 — 내가 만든 가짜 서버 둘 + 남이 만든 **진짜 공식 서버** 하나.
  - 승인 응답이 y/n 둘이 아니라 **y/n/a** — a(always) 를 고르면 그 도구는 이후 다시 안 묻는다.
  - 질문도 하나가 아니라 **여러 개**를 연속으로 물어서, 안전한 것과 위험한 것이 섞여 있을 때
    실제로 뭐가 자동 통과되고 뭐가 멈추는지 한 번에 확인한다.

붙이는 서버 3개:
  - "docs"  = server.py   (가짜 문서함 — list_files/read_file/delete_file/send_email)
  - "utils" = server2.py  (get_date/get_time + get_stock_price — yfinance로 실제 외부 API 호출)
  - "fs"    = 공식 filesystem MCP 서버(npx) — **진짜로 디스크에 접근하는** 유일한 서버.
              데모용 임시 폴더 하나만 허용 디렉토리로 열어준다.

⚠️ 도구 이름 충돌 주의: "docs" 서버의 read_file 과 "fs" 서버의 read_file 은 **이름이 같다.**
   MultiServerMCPClient.get_tools() 는 서버별로 이름을 구분해주지 않고 그냥 다 합친 리스트를
   돌려준다 — 그러면 에이전트에 바인딩될 때 **나중에 등록된 쪽(fs)이 조용히 이긴다.** 그래서
   이 데모에서는 read_file 을 아예 안 쓰고, fs 서버 쪽은 이름이 겹치지 않는 list_directory 로만
   확인한다(실전에서 여러 서버를 합칠 때 반드시 염두에 둬야 할 실제 위험이다).

준비:
  pip install mcp langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv yfinance
  Node.js 18+ (fs 서버가 npx 로 실행됨)
  .env 에 OPENAI_API_KEY

실행:
  python 5.total_hitl.py
"""

import asyncio
import os
import tempfile

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))

# ─── 위험한 도구 목록 (블랙리스트) ───────────────────────────────
#   실전에선 화이트리스트가 더 안전하다(2.risky_only.py 하단 메모 참고) — 여기선 도구 수가
#   많지 않아 "뭐가 위험한지" 눈으로 바로 보이는 블랙리스트를 그대로 썼다.
RISKY_TOOLS = {
    "delete_file",       # docs — 되돌릴 수 없는 삭제
    "send_email",        # docs — 한 번 나가면 회수 불가
    "get_stock_price",   # utils — 외부 API(yfinance)로 실제 네트워크 호출
    "list_directory",    # fs   — 진짜 디스크 접근
    "read_file",         # fs 쪽 read_file 이 이기므로(위 docstring 참고) 안전망으로 포함
}

SYSTEM_PROMPT = """너는 비서다. 사용자의 요청을 도구로 처리한다.
날짜/시간/주가 조회, 문서함 조회, 실제 폴더 조회처럼 필요한 도구를 알아서 골라 쓴다.
파일시스템 도구를 쓸 때는 read_file 대신 list_directory 를 우선 사용한다.
답변은 한국어로 간결하게 한다."""


def ask_approval(call) -> str:
    """도구 호출 하나를 보여주고 y/n/a 중 하나를 받는다. a = 이 도구는 이후 항상 허용."""
    print(f"\n  ⚠️  승인 필요: {call['name']}({call['args']})")
    while True:
        resp = input("      실행할까요? (y/n/a=항상 허용): ").strip().lower()
        if resp in ("y", "n", "a"):
            return resp
        print("      y / n / a 중 하나만 입력하세요.")


def mcp_config(work_dir: str) -> dict:
    return {
        "docs": {
            "command": "python", "args": [os.path.join(HERE, "server.py")],
            "transport": "stdio",
        },
        "utils": {
            "command": "python", "args": [os.path.join(HERE, "server2.py")],
            "transport": "stdio",
        },
        "fs": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", work_dir],
            "transport": "stdio",
        },
    }


async def main():
    # ─── fs 서버가 접근할 진짜(하지만 임시인) 폴더 준비 ────────────
    work_dir = tempfile.mkdtemp(prefix="mcp_total_hitl_")
    with open(os.path.join(work_dir, "note.txt"), "w", encoding="utf-8") as f:
        f.write("실제 파일시스템 서버가 보는 진짜 파일입니다.")
    print(f"[fs 서버 허용 디렉토리] {work_dir}\n")

    QUESTIONS = [
        "지금 날짜가 며칠이야?",                                  # get_date — 안전, 자동 통과
        "지금 몇 시야?",                                          # get_time — 안전, 자동 통과
        "지금 날짜랑 시간 둘 다 알려줘",                          # get_date+get_time 동시 호출 — 안전
        "문서함에 어떤 파일이 있는지 보여줘",                      # list_files — 안전
        "테슬라(TSLA) 주가 얼마야?",                              # get_stock_price — 위험, 첫 승인
        "이번엔 애플(AAPL) 주가도 알려줘",                        # get_stock_price 재호출 — a 선택시 재질문 없음
        f"{work_dir} 폴더 안에 어떤 파일이 있는지 list_directory 로 확인해줘",  # fs 서버 — 위험, 진짜 디스크
        "old_backup.zip 파일 지워줘",                             # delete_file — 위험
    ]

    tools = await MultiServerMCPClient(mcp_config(work_dir)).get_tools()
    print("붙은 도구:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(
        llm, tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
        interrupt_before=["tools"],
    )
    config = {"configurable": {"thread_id": "total-hitl-demo"}}

    # ─── 세션 동안 "항상 허용" 한 도구 이름들 — 질문이 바뀌어도 안 지워진다 ──
    ALLOWED_TOOLS: set[str] = set()

    for i, question in enumerate(QUESTIONS, start=1):
        print("=" * 66)
        print(f"[{i}/{len(QUESTIONS)}] [user] {question}")
        print("=" * 66)

        result = await agent.ainvoke({"messages": [("user", question)]}, config=config)
        shown = len(result["messages"])

        while result["messages"][-1].tool_calls:
            calls = result["messages"][-1].tool_calls
            rejected_ids = set()

            for call in calls:
                name = call["name"]
                if name in ALLOWED_TOOLS:
                    print(f"\n  ✓ 자동 허용(always): {name}({call['args']})")
                elif name not in RISKY_TOOLS:
                    print(f"\n  ✓ 자동 통과(안전): {name}({call['args']})")
                else:
                    resp = ask_approval(call)
                    if resp == "a":
                        ALLOWED_TOOLS.add(name)
                        print(f"      → '{name}' 은 이제부터 다시 안 묻는다.")
                    elif resp == "n":
                        rejected_ids.add(call["id"])
                        print("      → 거부됨.")

            if rejected_ids:
                messages = [
                    ToolMessage(
                        content=("사용자가 이 작업을 거부했습니다." if c["id"] in rejected_ids
                                 else "같은 요청의 다른 작업이 거부되어 함께 취소되었습니다."),
                        tool_call_id=c["id"], name=c["name"],
                    )
                    for c in calls
                ]
                agent.update_state(config, {"messages": messages}, as_node="tools")

            result = await agent.ainvoke(None, config=config)

            for m in result["messages"][shown:]:
                if m.type == "tool":
                    print(f"  ← {m.name}: {str(m.content)[:150]}")
            shown = len(result["messages"])

        print(f"\n[ai] {result['messages'][-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - 서버가 여러 개여도 승인 로직은 그대로다 — interrupt_before=["tools"] 는 어느 서버의
#     도구든 똑같이 잡아낸다. "내가 만든 서버"와 "남이 만든 공식 서버"를 구분 안 해도 된다.
#   - y/n/a — a 는 "이 세션 동안"만 유효한 화이트리스트를 그때그때 만드는 것이다. 재시작하면
#     ALLOWED_TOOLS 는 초기화된다(영구 저장하려면 파일/DB에 남겨야 한다).
#   - **a(always)는 '도구 이름' 단위다** — get_stock_price 를 한 번 always 허용하면, 그 뒤로는
#     어떤 종목을 조회하든(테슬라든 애플이든) 다시 안 묻는다. 인자별로 세밀하게 막고 싶다면
#     ALLOWED_TOOLS 를 (도구명, 인자) 조합으로 바꿔야 한다 — 8.exaone40, 18.mcp_ops_hitl
#     의 "자동승인이 너무 넓다"는 한계와 같은 이야기다.
#   - **도구 이름 충돌**: docs 서버와 fs 서버 둘 다 read_file 을 갖고 있다. 이 파일의 실측으로도
#     확인됐다 — 여러 MCP 서버를 한 에이전트에 동시에 붙일 때는 이름이 겹치는 도구가 없는지
#     반드시 확인해야 한다(이름이 같으면 나중에 등록한 서버가 조용히 이긴다).
