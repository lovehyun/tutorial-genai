# app.py — [3c] 병렬 계획은 그대로 두고, 위험한 호출만 하나씩 따로 승인받는다.
#
# ══ 이 폴더는 3단계의 세 변형(a/b/c) 중 하나다 — ../README.md 참고 ═══════
#   a(순차)는 parallel_tool_calls=False 로 아예 못 몰리게 막았다 — 안전하지만
#   온보딩 하나에 승인이 4번 필요해 피로가 쌓인다.
#   b(병렬)는 모델이 한 턴에 여러 도구를 계획하면 승인 카드도 통째로 몰아서 보여준다 —
#   빠르지만 사람이 위험도를 구분 못 하고 한 번에 다 승인해 버릴 수 있다.
#   c(여기)는 절충이다: 모델이 여러 도구를 한 턴에 계획하는 건 그대로 두되(빠름),
#   그 배치를 우리가 직접 갈라서 — 안전한 건 자동 실행, 위험한 건 '하나씩'
#   따로 승인받는다. 카드에 항상 도구 하나만 뜬다는 점은 a 와 같지만,
#   모델이 계획을 다시 세우려고 매번 새 턴을 도는 왕복이 없어서 더 빠르다.
#
# ══ 어떻게 다른가 (구현) ══════════════════════════════════════════
#   a/b 는 LangGraph 의 tools 노드가 이 턴의 tool_calls 를 통째로 실행하게 두고,
#   거부할 때만 as_node="tools" 로 끼어들었다. c 는 이 턴의 tool_calls 를
#   **처음부터 우리가 직접 하나씩** 처리한다 — 안전한 건 바로 tool.ainvoke(),
#   위험한 건 승인/거부를 기다린 뒤 tool.ainvoke() 또는 거부 메시지 — 그 결과를
#   전부 모아서 한 번에 as_node="tools" 로 주입하고 재개한다. tools 노드 자체는
#   이 턴에서 한 번도 안 불린다(이미 우리가 다 처리했으니).
#
# ══ 2단계의 한계 ═══════════════════════════════════════════════
#   2단계는 승인 카드가 뜨면 대화가 그 자리에서 멈춘다. 승인할 때까지 아무것도 못 한다.
#   실제 업무는 그렇지 않다 — "윤도현 온보딩 해줘" 를 시켜놓고 다른 일을 하다가,
#   승인이 필요한 순간에만 결정해 주면 된다.
#
# ══ 구조: 메인 에이전트 + 워커(서브에이전트) ════════════════════
#
#     사용자 ──대화──▶ 메인 에이전트   (조회 도구 + delegate_task/list_jobs)
#                          │ delegate_task("윤도현 온보딩")
#                          ▼
#                      작업 큐 ──▶ 워커 에이전트 (MCP 도구 전부)  ← 백그라운드 루프에서 실행
#                          │           │ 이 턴의 호출들을 하나씩 순회 — 안전은 바로,
#                          │           │ 위험은 정지하고 승인 대기
#                          │           ▼
#                          └──▶ 작업 패널에 "승인 대기"(도구 하나) 표시 ──▶ 사용자가 승인/거부
#                                                                    │
#                                            asyncio.Event 로 워커가 깨어나 다음 호출로 진행
#
#   메인과 워커는 thread_id 가 다르다 = 완전히 분리된 대화다.
#   워커가 여러 개면 각자 자기 thread_id 로 동시에 진행하고, 각자 따로 승인을 기다린다.
#
# 실행:
#   pip install flask langchain langchain-openai langchain-mcp-adapters langgraph \
#               langgraph-checkpoint-sqlite python-dotenv mcp
#   .env 에 OPENAI_API_KEY
#   python app.py     → http://localhost:5087

import asyncio
import os
import threading
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "..", "servers")
CHECKPOINT_DB = os.path.join(HERE, "checkpoints.sqlite")

SAFE_TOOLS = {"find_employee", "get_account_status", "list_groups", "list_sent"}

MAIN_SYSTEM = """너는 사내 IT 헬프데스크 접수 담당이다.

직접 할 수 있는 일: 직원·계정·그룹 조회 (find_employee, get_account_status, list_groups)
직접 하지 않는 일: 계정 생성, 권한 부여, 비밀번호 초기화, 메일 발송

계정을 바꾸거나 알림을 보내는 '작업' 요청이 오면 직접 하려 하지 말고
delegate_task 도구로 담당자에게 위임하라. 위임하면 작업 번호가 나오는데,
사용자에게 그 번호를 알려주고 "오른쪽 작업 패널에서 진행 상황과 승인 요청을 확인하라" 고 안내하라.

delegate_task 의 instruction 에는 담당자가 혼자 읽고 처리할 수 있도록
대상(사번 또는 이름), 해야 할 일, 조건을 빠짐없이 적어라.

진행 상황을 물으면 list_jobs 로 확인해 알려준다.
답변은 한국어로 간결하게."""

WORKER_SYSTEM = """너는 사내 IT 운영 담당자다. 배정받은 작업 지시를 처리한다.

규칙:
- 사번을 모르면 find_employee 로 먼저 찾는다. 추측한 사번을 쓰지 않는다.
- 계정이 없으면 create_account 를 먼저 하고 권한을 부여한다.
- 관리자가 어떤 작업을 거부하면 다시 시도하지 않는다. 나머지 작업은 이어서 하고,
  마지막에 무엇을 했고 무엇이 거부됐는지 보고한다.
- 요청에 맞는 도구가 없으면 "그 작업을 할 수 있는 도구가 없다" 고 그대로 말한다.
  "승인이 필요하다" 거나 "거부되었다" 는 식으로 이유를 지어내지 않는다.
  승인·거부는 실제로 승인 절차를 거친 작업에 대해서만 언급한다.
- 작업이 끝나면 처리 결과를 한국어로 3줄 이내로 요약한다."""


# ══════════════════════════════════════════════════════════════
# 전용 이벤트 루프 — 채팅과 모든 워커가 여기서 함께 돌아간다
# ══════════════════════════════════════════════════════════════

LOOP = asyncio.new_event_loop()
threading.Thread(target=LOOP.run_forever, daemon=True).start()


def run(coro):
    """Flask 요청 스레드 → 백그라운드 루프. 결과를 기다린다(채팅용)."""
    return asyncio.run_coroutine_threadsafe(coro, LOOP).result()


def spawn(coro):
    """결과를 기다리지 않고 백그라운드 루프에 던져둔다(워커용)."""
    asyncio.run_coroutine_threadsafe(coro, LOOP)


# ══════════════════════════════════════════════════════════════
# 작업 저장소
# ══════════════════════════════════════════════════════════════

JOBS = {}            # job_id -> dict
JOB_SEQ = 0
JOB_LOCK = threading.Lock()

# 이 실행에만 해당하는 식별자. 작업 스레드 id 앞에 붙인다.
#   체크포인터는 파일(checkpoints.sqlite)에 남으므로, 앱을 재시작하면 JOB_SEQ 는 0 으로
#   돌아가는데 'job-J001' 체크포인트는 그대로 남아 있다. 그대로 쓰면 새 작업이
#   옛날 대화를 이어받아 "이미 처리했다" 며 도구를 안 부른다. RUN_ID 로 그걸 막는다.
RUN_ID = uuid.uuid4().hex[:8]


def new_job(title: str, instruction: str) -> str:
    global JOB_SEQ
    with JOB_LOCK:
        JOB_SEQ += 1
        job_id = f"J{JOB_SEQ:03d}"
    JOBS[job_id] = {
        "id": job_id,
        "title": title,
        "instruction": instruction,
        "status": "queued",        # queued → running → waiting → done / rejected / error
        "log": [],
        "pending": None,           # 승인 대기 중인 도구 호출 — [3c] 이 배치에서 지금 보고 있는 것 '하나'
        "result": "",
        "_event": None,            # 워커를 깨우는 신호
        "_decision": None,         # True(승인) / False(거부)
    }
    return job_id


def public(job: dict) -> dict:
    """밑줄로 시작하는 내부 필드(_event 등)는 JSON 으로 내보내지 않는다."""
    return {k: v for k, v in job.items() if not k.startswith("_")}


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
        cm = AsyncSqliteSaver.from_conn_string(CHECKPOINT_DB)
        saver = await cm.__aenter__()
        globals()["_CHECKPOINT_CM"] = cm
        print(f"[체크포인터] SQLite 영속 — {CHECKPOINT_DB}")
        return saver
    except Exception as e:
        print(f"[체크포인터] 메모리 폴백 ({type(e).__name__}: {e})")
        print("             → pip install langgraph-checkpoint-sqlite 하면 영속으로 바뀐다.")
        return MemorySaver()


# ── 메인 에이전트가 쓰는 로컬 도구 (MCP 아님) ───────────────────

@tool
def delegate_task(title: str, instruction: str) -> str:
    """
    계정 변경·권한 부여·알림 발송처럼 시간이 걸리는 업무를 담당자에게 위임한다.
    즉시 작업 번호를 돌려주고, 실제 처리는 백그라운드에서 진행된다.

    Args:
        title: 작업 제목 (예: '윤도현 온보딩')
        instruction: 담당자가 혼자 읽고 처리할 수 있는 구체적 지시.
                     대상(사번 또는 이름), 해야 할 일, 조건을 모두 포함한다.

    Returns:
        배정된 작업 번호
    """
    job_id = new_job(title, instruction)
    spawn(run_job(job_id))          # 여기서 기다리지 않는다 — 던져놓고 바로 반환
    return f"작업 {job_id} 을 담당자에게 배정했습니다. 진행 상황은 작업 패널에서 확인하세요."


@tool
def list_jobs() -> str:
    """진행 중이거나 완료된 위임 작업의 목록과 상태를 조회한다."""
    if not JOBS:
        return "위임된 작업이 없습니다."
    label = {"queued": "대기", "running": "진행 중", "waiting": "승인 대기",
             "done": "완료", "rejected": "거부됨", "error": "오류"}
    return "\n".join(
        f"{j['id']} | {j['title']} | {label.get(j['status'], j['status'])}"
        for j in JOBS.values()
    )


# ══════════════════════════════════════════════════════════════
# [3c] 도구 직접 실행 — tools 노드를 거치지 않고 우리가 직접 부른다
# ══════════════════════════════════════════════════════════════

TOOLS_BY_NAME = {}   # build() 에서 채운다


async def _invoke_tool(call) -> ToolMessage:
    """도구 하나를 실제로 실행하고 ToolMessage 로 감싼다.

    ToolNode 가 내부적으로 하는 것과 같은 일(tool.ainvoke)을 우리가 대신 한다 —
    그래야 이 배치를 '안전은 즉시, 위험은 하나씩'으로 쪼갤 수 있다.
    """
    tool_obj = TOOLS_BY_NAME[call["name"]]
    try:
        result = await tool_obj.ainvoke(call["args"])
    except Exception as e:
        result = f"도구 실행 오류: {type(e).__name__}: {e}"
    return ToolMessage(content=result, tool_call_id=call["id"], name=call["name"])


# ══════════════════════════════════════════════════════════════
# 워커 — 작업 하나를 끝까지(또는 승인 대기까지) 밀고 나간다
# ══════════════════════════════════════════════════════════════

def collect(messages, start: int) -> list:
    out = []
    for m in messages[start:]:
        for c in (getattr(m, "tool_calls", None) or []):
            out.append(f"→ {c['name']}({c['args']})")
        if m.type == "tool":
            out.append(f"← {m.name}: {str(m.content)[:160]}")
    return out


async def run_job(job_id: str) -> None:
    job = JOBS[job_id]
    config = {"configurable": {"thread_id": f"job-{RUN_ID}-{job_id}"}}   # 작업마다 독립된 대화
    job["status"] = "running"

    try:
        state = await worker.ainvoke({"messages": [("user", job["instruction"])]}, config=config)
        job["log"].extend(collect(state["messages"], 0))

        while True:
            calls = getattr(state["messages"][-1], "tool_calls", None)

            if not calls:                                   # 최종 답변 = 작업 완료
                job["status"] = "done"
                job["result"] = state["messages"][-1].content
                job["log"].append("✔ 작업 완료")
                return

            # [3c] 이 턴에 몰려온 호출을 우리가 직접 하나씩 처리한다.
            #   안전한 건 바로 실행, 위험한 건 딱 하나만 승인 대기로 보여준다 —
            #   b 처럼 여러 개를 한 카드에 몰아서 보여주지 않는다.
            results = {}   # tool_call_id -> ToolMessage

            for c in calls:
                if c["name"] in SAFE_TOOLS:
                    results[c["id"]] = await _invoke_tool(c)
                    job["log"].append(f"⚙ 자동 실행(조회): {c['name']}")
                    continue

                # ── 승인 대기 (이 호출 하나만) ──────────────────
                #   Event 를 만들어 두고 잠든다. 스레드를 붙잡지 않으므로
                #   그 사이 채팅도 다른 워커도 같은 루프에서 계속 돌아간다.
                job["pending"] = [{"name": c["name"], "args": c["args"]}]
                job["status"] = "waiting"
                job["_event"] = asyncio.Event()
                await job["_event"].wait()                  # ← 여기서 잠든다

                approved = job["_decision"]
                job["pending"] = None
                job["_event"] = None
                job["status"] = "running"

                if approved:
                    results[c["id"]] = await _invoke_tool(c)
                    job["log"].append(f"✓ 승인 후 실행: {c['name']}")
                else:
                    results[c["id"]] = ToolMessage(
                        content="관리자가 이 작업을 거부했습니다. 실행하지 않았습니다.",
                        tool_call_id=c["id"], name=c["name"],
                    )
                    job["log"].append(f"✗ 거부됨: {c['name']}")

            # 이 턴의 모든 tool_call_id 에 결과가 모였다 — tools 노드는 건너뛰고
            # 우리가 만든 결과를 그대로 주입한다 (순서는 calls 순서를 그대로 따른다).
            before = len(state["messages"])
            await worker.aupdate_state(
                config,
                {"messages": [results[c["id"]] for c in calls]},
                as_node="tools",
            )
            state = await worker.ainvoke(None, config=config)
            job["log"].extend(collect(state["messages"], before))

    except Exception as e:
        job["status"] = "error"
        job["result"] = f"{type(e).__name__}: {e}"
        job["log"].append(f"✗ 오류: {job['result']}")


# ══════════════════════════════════════════════════════════════
# 조립
# ══════════════════════════════════════════════════════════════

async def build():
    tools = await MultiServerMCPClient(mcp_config()).get_tools()
    TOOLS_BY_NAME.update({t.name: t for t in tools})

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    checkpointer = await make_checkpointer()

    # 워커: MCP 도구 전부. interrupt_before 는 그대로 쓰지만, run_job 이 매번
    # 결과를 직접 주입하므로 tools 노드는 사실상 절대 실행되지 않는다.
    worker_agent = create_agent(
        llm, tools,
        system_prompt=WORKER_SYSTEM,
        checkpointer=checkpointer,
        interrupt_before=["tools"],
    )

    # 메인: 조회 도구만 + 위임/조회용 로컬 도구. 정지하지 않는다(대화가 끊기면 안 되므로)
    read_only = [t for t in tools if t.name in SAFE_TOOLS]
    main_agent = create_agent(
        llm, read_only + [delegate_task, list_jobs],
        system_prompt=MAIN_SYSTEM,
        checkpointer=MemorySaver(),
    )
    return main_agent, worker_agent, [t.name for t in tools]


main, worker, TOOL_NAMES = run(build())

app = Flask(__name__)
CHAT_CONFIG = {"configurable": {"thread_id": "web"}}


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
        return jsonify({"reply": "메시지를 입력하세요.", "trace": []})

    async def turn():
        snapshot = await main.aget_state(CHAT_CONFIG)
        before = len(snapshot.values.get("messages", []))
        state = await main.ainvoke({"messages": [("user", message)]}, config=CHAT_CONFIG)
        trace = []
        for m in state["messages"][before:]:
            for c in (getattr(m, "tool_calls", None) or []):
                trace.append(f"→ {c['name']}({c['args']})")
            if m.type == "tool":
                trace.append(f"← {m.name}: {str(m.content)[:200]}")
        return {"reply": state["messages"][-1].content, "trace": trace}

    return jsonify(run(turn()))


@app.route("/jobs")
def jobs():
    """작업 패널이 1초마다 폴링한다. 승인 대기가 생기면 여기서 발견된다."""
    return jsonify({"jobs": [public(j) for j in JOBS.values()]})


@app.route("/jobs/<job_id>/decide", methods=["POST"])
def decide(job_id):
    """승인/거부 버튼. 잠들어 있는 워커를 깨운다."""
    job = JOBS.get(job_id)
    if not job or job["status"] != "waiting":
        return jsonify({"ok": False, "error": "승인 대기 중인 작업이 아닙니다."}), 400

    job["_decision"] = bool((request.json or {}).get("approved"))
    event = job["_event"]
    if event:
        # Event 는 백그라운드 루프의 것이므로, 그 루프 안에서 set 해야 안전하다
        LOOP.call_soon_threadsafe(event.set)
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("MCP 도구:", TOOL_NAMES)
    print("메인 에이전트: 조회 도구 + delegate_task / list_jobs")
    print("워커 에이전트: MCP 도구 전부 (한 턴에 여러 개를 계획해도, 위험한 건 하나씩 승인)")
    print("→ http://localhost:5087")
    app.run(port=5087, debug=False, threaded=True)
