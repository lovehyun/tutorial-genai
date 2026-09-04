# agents.py — MCP 연결과 에이전트 조립
#
# 1~3단계에서 이미 만든 것들이다. 4단계에서 바뀐 것이 없어서 통째로 빼뒀다.
#   · mcp_config()      : 서버 3개를 stdio 로 띄우는 설정 (1단계 그대로)
#   · make_checkpointer(): 승인 대기를 저장할 곳 (2단계 그대로)
#   · build()           : 메인/워커 두 에이전트로 분리 (3단계 그대로)

import os

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

import jobs

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "servers")
CHECKPOINT_DB = os.path.join(HERE, "checkpoints.sqlite")

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
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    checkpointer = await make_checkpointer()

    # 워커: MCP 도구 전부 + 위험한 도구에서 정지
    worker_agent = create_agent(
        llm, tools,
        system_prompt=WORKER_SYSTEM,
        checkpointer=checkpointer,
        interrupt_before=["tools"],
    )

    # 메인: 조회 도구만 + 위임/조회용 로컬 도구. 정지하지 않는다(대화가 끊기면 안 되므로)
    read_only = [t for t in tools if t.name in jobs.SAFE_TOOLS]
    main_agent = create_agent(
        llm, read_only + [jobs.delegate_task, jobs.list_jobs],
        system_prompt=MAIN_SYSTEM,
        checkpointer=MemorySaver(),
    )
    return main_agent, worker_agent, [t.name for t in tools]
