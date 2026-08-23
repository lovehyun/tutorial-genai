# app.py — [2단계] 되돌릴 수 없는 작업 앞에서 멈추고, 웹 화면으로 승인받는다.
#
# ══ 이 폴더에 대해 ══════════════════════════════════════════════
#   4b.hitl_approval_client.py(CLI)의 웹 버전. 4시간 안에 다 못 다룰 수 있어
#   instructor 전용 보너스로만 넣었다(student(todo)/answer 에는 없음).
#   원본: 10.project/15.mcp_ops_assistant/2.hitl_approve/ (+ 공유 servers/)
#   실행: pip install flask langgraph-checkpoint-sqlite (+ 4b와 같은 의존성) 후
#         이 폴더에 .env(OPENAI_API_KEY) 넣고 python app.py → http://localhost:5082
#
# ══ 이 단계의 핵심: 웹에는 input() 이 없다 ══════════════════════
#
#   CLI 라면 input() 으로 그 자리에서 멈추면 된다. 프로세스가 통째로 기다린다.
#   웹은 요청/응답이라 블로킹할 수 없다. 그럼 어떻게 '기다리게' 하나?
#
#     ① 에이전트가 도구 호출 직전에 멈춘다        (interrupt_before=["tools"])
#     ② 멈춘 상태가 checkpointer 에 통째로 저장된다  ← 이게 전부를 가능하게 한다
#     ③ /chat 은 "승인 대기" 라고 응답하고 끝난다  (연결을 붙잡지 않는다)
#     ④ 사용자가 승인 버튼을 누르면 /approve 가 그 상태를 꺼내 재개한다
#
#   즉 '기다림' 을 프로세스가 아니라 저장소가 담당한다.
#   thread_id 는 사실상 작업 티켓 번호이고, 영속 체크포인터를 쓰면
#   브라우저를 닫아도 서버를 재시작해도 승인 대기가 살아남는다.
#
# ══ 두 번째 포인트: 전용 이벤트 루프 스레드 ═════════════════════
#
#   1단계는 요청마다 asyncio.run() 을 새로 돌렸다. 그래도 됐던 이유는
#   상태를 요청 사이에 들고 있을 필요가 없었기 때문이다.
#   2단계부터는 체크포인터(비동기 DB 커넥션)가 요청을 넘어 살아 있어야 한다.
#   → 백그라운드 스레드에 이벤트 루프를 하나 띄워두고, Flask 는 거기에 일을 맡긴다.
#     (3단계에서 이 루프가 백그라운드 작업까지 굴린다)
#
# 실행:
#   pip install flask langchain langchain-openai langchain-mcp-adapters langgraph \
#               langgraph-checkpoint-sqlite python-dotenv mcp
#   .env 에 OPENAI_API_KEY
#   python app.py     → http://localhost:5082

import asyncio
import os
import threading

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "servers")  # 원본은 ../servers(형제 폴더 공유) — 여기선 이 폴더 안에 같이 둠
CHECKPOINT_DB = os.path.join(HERE, "checkpoints.sqlite")

# ── 승인이 필요한 도구 ──────────────────────────────────────────
#   화이트리스트(안전한 것만 나열)로 관리한다. 블랙리스트로 하면
#   MCP 서버에 새 도구가 생겼을 때 '모르는 도구' 가 무사통과한다.
SAFE_TOOLS = {"find_employee", "get_account_status", "list_groups", "list_sent"}

SYSTEM = """너는 사내 IT 헬프데스크 비서다. 세 시스템의 도구를 쓸 수 있다.

- 인사/계정 조회: find_employee, get_account_status, list_groups
- 계정 조치:      create_account, grant_access, revoke_access, reset_password
- 알림:           send_email, post_message, list_sent

규칙:
- 사번을 모르면 find_employee 로 먼저 찾는다. 추측한 사번을 쓰지 않는다.
- 계정이 없으면 create_account 를 먼저 하고 권한을 부여한다.
- 관리자가 어떤 작업을 거부하면 존중하고 다시 시도하지 않는다.
  대신 왜 거부했는지 묻거나, 할 수 있는 다른 방법을 한 가지 제안한다.
- 요청에 맞는 도구가 없으면 "그 작업을 할 수 있는 도구가 없다" 고 그대로 말한다.
  "승인이 필요하다" 거나 "거부되었다" 는 식으로 이유를 지어내지 않는다.
  승인·거부는 실제로 승인 절차를 거친 작업에 대해서만 언급한다.
- 답변은 한국어로, 무엇을 했고 무엇을 못 했는지 사실 그대로 정리한다."""


# ══════════════════════════════════════════════════════════════
# 전용 이벤트 루프 — Flask(동기) 와 에이전트(비동기)를 잇는 다리
# ══════════════════════════════════════════════════════════════

LOOP = asyncio.new_event_loop()
threading.Thread(target=LOOP.run_forever, daemon=True).start()


def run(coro):
    """Flask 요청 스레드 → 백그라운드 루프. 결과를 기다린다(채팅용)."""
    return asyncio.run_coroutine_threadsafe(coro, LOOP).result()


# ══════════════════════════════════════════════════════════════
# 에이전트 준비
# ══════════════════════════════════════════════════════════════

def mcp_config() -> dict:
    """세 MCP 서버를 stdio 로 띄우는 설정. 1~4단계가 모두 이 설정을 똑같이 쓴다."""
    return {
        "directory": {"command": "python",
                      "args": [os.path.join(SERVERS, "directory_server.py")],
                      "transport": "stdio"},
        "itops":     {"command": "python",
                      "args": [os.path.join(SERVERS, "itops_server.py")],
                      "transport": "stdio"},
        "notify":    {"command": "python",
                      "args": [os.path.join(SERVERS, "notify_server.py")],
                      "transport": "stdio"},
    }


async def make_checkpointer():
    """영속 체크포인터. 없으면 메모리로 물러선다."""
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        # from_conn_string 은 async context manager 다.
        # 앱이 살아 있는 동안 계속 써야 하므로 수동으로 진입시켜 붙잡아 둔다.
        cm = AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB)
        saver = await cm.__aenter__()
        globals()["_CHECKPOINT_CM"] = cm
        print(f"[체크포인터] SQLite 영속 — {CHECKPOINT_DB}")
        return saver
    except Exception as e:
        print(f"[체크포인터] 메모리 폴백 ({type(e).__name__}: {e})")
        print("             → pip install langgraph-checkpoint-sqlite 하면 영속으로 바뀐다.")
        return MemorySaver()


async def build():
    tools = await MultiServerMCPClient(mcp_config()).get_tools()
    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        system_prompt=SYSTEM,
        checkpointer=await make_checkpointer(),
        interrupt_before=["tools"],       # ← 도구 호출 직전마다 정지
    )
    return agent, [t.name for t in tools]


agent, TOOL_NAMES = run(build())

app = Flask(__name__)
CONFIG = {"configurable": {"thread_id": "web"}}     # 데모라 대화 하나. 실제로는 사용자별로 발급


# ══════════════════════════════════════════════════════════════
# 에이전트 구동 — '끝날 때까지' 가 아니라 '멈춰야 할 곳까지' 돌린다
# ══════════════════════════════════════════════════════════════

def collect(messages, start: int) -> list:
    out = []
    for m in messages[start:]:
        for c in (getattr(m, "tool_calls", None) or []):
            out.append(f"→ {c['name']}({c['args']})")
        if m.type == "tool":
            out.append(f"← {m.name}: {str(m.content)[:160]}")
    return out


async def drive(state, trace: list) -> dict:
    """
    안전한 도구는 알아서 실행하고, 위험한 도구를 만나면 멈춰서 승인을 요청한다.

    반환:
      {"state": "done",    "reply": ...}      최종 답변까지 도달
      {"state": "pending", "calls": [...]}    승인 대기 (여기서 함수가 끝난다 — 기다리지 않는다)
    """
    while True:
        calls = getattr(state["messages"][-1], "tool_calls", None)

        if not calls:                                   # 부를 도구가 없다 = 최종 답변
            return {"state": "done", "reply": state["messages"][-1].content, "trace": trace}

        risky = [c for c in calls if c["name"] not in SAFE_TOOLS]
        if risky:
            # 승인 대기 상태로 '남겨둔' 채 응답한다.
            # 에이전트는 checkpointer 안에 멈춰 있고, /approve 가 올 때까지 아무 일도 안 한다.
            return {
                "state": "pending",
                "calls": [{"name": c["name"], "args": c["args"]} for c in calls],
                "trace": trace,
            }

        # 조회 도구뿐이면 묻지 않고 그대로 진행한다 (승인 피로를 막는 핵심)
        before = len(state["messages"])
        state = await agent.ainvoke(None, config=CONFIG)
        trace.extend(collect(state["messages"], before))


async def start_turn(message: str) -> dict:
    # 비동기 체크포인터를 쓰므로 상태 조회도 비동기 API 를 써야 한다 (get_state ✗ / aget_state ○)
    snapshot = await agent.aget_state(CONFIG)
    before = len(snapshot.values.get("messages", []))
    state = await agent.ainvoke({"messages": [("user", message)]}, config=CONFIG)
    return await drive(state, collect(state["messages"], before))


async def resume(approved: bool) -> dict:
    """승인/거부 결정을 반영하고 멈춰 있던 에이전트를 이어서 돌린다."""
    snapshot = await agent.aget_state(CONFIG)
    calls = snapshot.values["messages"][-1].tool_calls
    before = len(snapshot.values["messages"])
    trace = []

    if not approved:
        # ── 거부 처리 ──────────────────────────────────────────
        #   as_node="tools" 가 핵심이다. 이게 없으면 상태에 메시지만 얹히고
        #   도구는 그대로 실행돼 버린다. 이걸 줘야 tools 노드를 '이미 실행한 것' 으로
        #   치고 건너뛴다. tool_call 하나당 결과 하나를 맞춰야 다음 LLM 호출이 깨지지 않는다.
        await agent.aupdate_state(
            CONFIG,
            {"messages": [
                ToolMessage(content="관리자가 이 작업을 거부했습니다. 실행하지 않았습니다.",
                            tool_call_id=c["id"], name=c["name"])
                for c in calls
            ]},
            as_node="tools",
        )
        trace.append(f"✗ 거부됨: {', '.join(c['name'] for c in calls)}")

    state = await agent.ainvoke(None, config=CONFIG)
    trace.extend(collect(state["messages"], before))
    return await drive(state, trace)


# ══════════════════════════════════════════════════════════════
# 엔드포인트
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html", tools=TOOL_NAMES, safe=sorted(SAFE_TOOLS))


@app.route("/chat", methods=["POST"])
def chat():
    message = (request.json or {}).get("message", "").strip()
    if not message:
        return jsonify({"state": "done", "reply": "메시지를 입력하세요.", "trace": []})
    return jsonify(run(start_turn(message)))


@app.route("/approve", methods=["POST"])
def approve():
    """승인 카드의 버튼이 호출한다. 멈춰 있던 에이전트를 재개시킨다."""
    approved = bool((request.json or {}).get("approved"))
    return jsonify(run(resume(approved)))


if __name__ == "__main__":
    print("도구:", TOOL_NAMES)
    print("자동 통과:", sorted(SAFE_TOOLS))
    print("→ http://localhost:5082")
    app.run(port=5082, debug=False)
