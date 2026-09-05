# jobs.py — 백그라운드 작업 실행기
#
# a.tool_name_only/jobs.py 에 있던 것을 그대로 옮겼다. b(여기)에서 실제로 바뀐 곳은
# 한 군데뿐이다 — 아래 [4b] 주석을 찾아보면 된다.
#
#   a 의 한계: 자동승인이 '도구 이름' 단위였다. grant_access 를 한 번 자동승인하면
#   어떤 그룹(email 이든 prod-db 든)을 요청하든 그냥 나갔다 — 도구 이름만 보고, 그 도구가
#   지금 무엇에 쓰이는지(인자)는 안 봤기 때문이다.
#
#   b 에서 더하는 것: group 의 위험도(risk)가 high 면, grant_access 가 자동승인
#   목록에 있어도 이번엔 무시하고 다시 승인을 받는다. "도구 이름" 대신 "인자" 까지
#   보고 판단하는 것 — a.tool_name_only/CHANGES.md 에 아이디어로만 적혀 있던 걸 실제로 구현한 것이다.

import asyncio
import os
import sys
import threading
import uuid

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "..", "servers")
sys.path.insert(0, os.path.abspath(SERVERS))
import store  # noqa: E402  — group 별 위험도(risk)를 읽어오려고 필요하다


# ══════════════════════════════════════════════════════════════
# 전용 이벤트 루프 (a 와 동일)
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
# 승인 정책
# ══════════════════════════════════════════════════════════════

SAFE_TOOLS = {"find_employee", "get_account_status", "list_groups", "list_sent"}

# 자동승인된 도구 이름 — 비어 있는 채로 시작하고 [항상 승인] 을 누를 때만 늘어난다.
#   데모라 메모리에 둔다. 실무라면 '누가 언제 왜 등록했는지' 와 함께 DB 에 남긴다.
AUTO_APPROVED = set()

# [4b] group 이름 → 위험도. servers/store.py 의 시드 데이터를 그대로 참고한다
#   (여기 따로 하드코딩하면 store.py 가 바뀔 때 둘이 어긋날 수 있어서 그렇게 안 했다).
_GROUP_RISK = {name: risk for name, _desc, risk in store.GROUPS}


def _is_high_risk(call) -> bool:
    """[4b] 이 호출이 '인자로 보면' 고위험인가 — 지금은 grant_access + risk=high 그룹만 해당."""
    if call["name"] != "grant_access":
        return False
    return _GROUP_RISK.get(call["args"].get("group")) == "high"


def needs_approval(call) -> bool:
    """조회 도구도 아니고 자동승인도 안 된 것 = 물어봐야 하는 것.

    [4b] 단, 인자가 고위험이면 자동승인 목록에 있어도 예외 없이 다시 물어본다 —
    '도구 이름' 단위 자동승인의 구멍(a 의 한계)을 인자 조건으로 좁힌 것.
    """
    if call["name"] in SAFE_TOOLS:
        return False
    if _is_high_risk(call):
        return True
    return call["name"] not in AUTO_APPROVED


# ══════════════════════════════════════════════════════════════
# 작업 저장소 (a 와 동일)
# ══════════════════════════════════════════════════════════════

JOBS = {}
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
        "pending": None,           # 승인 대기 중인 도구 호출
        "locked": False,           # [4b] 고위험 인자가 섞여 있어 '항상 승인' 을 못 쓰게 함
        "result": "",
        "_event": None,            # 워커를 깨우는 신호
        "_decision": None,         # True(승인) / False(거부)
    }
    return job_id


def clear() -> None:
    """작업 목록을 비운다. 데모 초기화([초기화] 버튼)에서 부른다."""
    global JOB_SEQ
    with JOB_LOCK:
        JOBS.clear()
        JOB_SEQ = 0


def public(job: dict) -> dict:
    """밑줄로 시작하는 내부 필드(_event 등)는 JSON 으로 내보내지 않는다."""
    return {k: v for k, v in job.items() if not k.startswith("_")}


# ══════════════════════════════════════════════════════════════
# 워커
# ══════════════════════════════════════════════════════════════

# 워커 에이전트. app.py 가 조립한 뒤 bind() 로 넣어준다.
#   (이 모듈이 agents.py 를 import 하면 순환 참조가 되므로 반대로 주입받는다)
worker = None


def bind(agent) -> None:
    global worker
    worker = agent


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

            ask = [c for c in calls if needs_approval(c)]

            # 자동승인으로 통과한 것은 로그에 남긴다 (안 보이면 통제가 아니다)
            for c in calls:
                if c["name"] in AUTO_APPROVED and c not in ask:
                    job["log"].append(f"⚡ 자동승인: {c['name']}")

            if ask:
                job["pending"] = [{"name": c["name"], "args": c["args"]} for c in calls]
                # [4b] 이 배치에 고위험 인자가 하나라도 있으면 '항상 승인' 자체를 막는다.
                #   섞여 있는 걸 통째로 자동승인하게 두면 guardrail 의미가 없어진다.
                job["locked"] = any(_is_high_risk(c) for c in calls)
                job["status"] = "waiting"
                job["_event"] = asyncio.Event()
                await job["_event"].wait()                  # ← 여기서 잠든다

                approved = job["_decision"]
                job["pending"] = None
                job["locked"] = False
                job["_event"] = None
                job["status"] = "running"

                if not approved:
                    # 거부 — tools 노드를 건너뛰고 거부 사실을 결과로 주입한다.
                    # as_node="tools" 가 없으면 도구가 그대로 실행돼 버린다.
                    await worker.aupdate_state(
                        config,
                        {"messages": [
                            ToolMessage(content="관리자가 이 작업을 거부했습니다. 실행하지 않았습니다.",
                                        tool_call_id=c["id"], name=c["name"])
                            for c in calls
                        ]},
                        as_node="tools",
                    )
                    job["log"].append(f"✗ 거부됨: {', '.join(c['name'] for c in calls)}")

            before = len(state["messages"])
            state = await worker.ainvoke(None, config=config)
            job["log"].extend(collect(state["messages"], before))

    except Exception as e:
        job["status"] = "error"
        job["result"] = f"{type(e).__name__}: {e}"
        job["log"].append(f"✗ 오류: {job['result']}")


# ══════════════════════════════════════════════════════════════
# 메인 에이전트가 쓰는 로컬 도구 (MCP 아님) — a 와 동일
# ══════════════════════════════════════════════════════════════

@tool
def delegate_task(title: str, instruction: str) -> str:
    """
    계정 변경·권한 부여·알림 발송처럼 시간이 걸리는 업무를 담당자에게 위임한다.
    즉시 작업 번호를 돌려주고, 실제 처리는 백그라운드에서 진행된다.

    Args:
        title: 작업 제목 (예: '오지훈 온보딩')
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
