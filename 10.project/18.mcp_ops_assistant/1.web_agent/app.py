# app.py — [1단계] 웹 챗봇 + MCP 서버 3개. 승인 절차는 아직 없다.
#
# ── 이 단계에서 하는 것 ─────────────────────────────────────────
#   사내 업무(직원 조회 / 계정 생성 / 권한 부여 / 메일 발송)를 챗봇에게 말로 시킨다.
#   에이전트가 세 MCP 서버의 도구를 알아서 골라 처리한다.
#
# ── 이 단계의 문제 (2단계로 넘어가는 이유) ──────────────────────
#   "김철수한테 prod-db 권한 줘" 라고 하면 그냥 준다. 아무도 안 물어본다.
#   운영 DB 접근 권한이 대화 한 줄로 나가는 것이다.
#   → 되돌릴 수 없는 작업 앞에 사람을 세워야 한다. 그게 2.hitl_approve.
#
# 실행:
#   pip install flask langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv mcp
#   .env 에 OPENAI_API_KEY
#   python app.py     → http://localhost:5081

import asyncio
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVERS = os.path.join(HERE, "..", "servers")

SYSTEM = """너는 사내 IT 헬프데스크 비서다. 세 시스템의 도구를 쓸 수 있다.

- 인사/계정 조회: find_employee, get_account_status, list_groups
- 계정 조치:      create_account, grant_access, revoke_access, reset_password
- 알림:           send_email, post_message, list_sent

규칙:
- 사번을 모르면 find_employee 로 먼저 찾는다. 추측한 사번을 쓰지 않는다.
- 권한을 주기 전에 list_groups 로 그룹명이 맞는지 확인한다.
- 계정이 없으면 create_account 를 먼저 하고 권한을 부여한다.
- 도구가 오류 메시지를 돌려주면 그대로 사용자에게 알리고 어떻게 할지 묻는다.
- 답변은 한국어로, 무엇을 했는지 사실 그대로 간결하게 정리한다."""


def mcp_config() -> dict:
    """세 MCP 서버를 stdio 로 띄우는 설정. 1~3단계가 모두 이 설정을 똑같이 쓴다."""
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


async def build_agent():
    """세 서버의 도구를 한 묶음으로 받아 에이전트를 만든다."""
    tools = await MultiServerMCPClient(mcp_config()).get_tools()
    agent = create_agent(
        ChatOpenAI(model="gpt-4o-mini", temperature=0),
        tools,
        system_prompt=SYSTEM,
        checkpointer=MemorySaver(),     # 대화 이력 보관 → '그 사람' 같은 지시어가 통한다
    )
    return agent, [t.name for t in tools]


agent, TOOL_NAMES = asyncio.run(build_agent())

app = Flask(__name__)

# 데모라 대화는 하나만 쓴다. 실제 서비스라면 로그인 사용자별로 발급한다.
CONFIG = {"configurable": {"thread_id": "web"}}


@app.route("/")
def index():
    return render_template("index.html", tools=TOOL_NAMES)


@app.route("/chat", methods=["POST"])
def chat():
    message = (request.json or {}).get("message", "").strip()
    if not message:
        return jsonify({"reply": "메시지를 입력하세요.", "trace": []})

    before = len(agent.get_state(CONFIG).values.get("messages", []))
    result = asyncio.run(agent.ainvoke({"messages": [("user", message)]}, config=CONFIG))

    # 이번 턴에 새로 생긴 메시지만 훑어 도구 호출/결과를 뽑는다
    # (messages 는 append-only 라서 인덱스 하나로 '이번 것' 을 가려낼 수 있다)
    trace = []
    for m in result["messages"][before:]:
        for c in (getattr(m, "tool_calls", None) or []):
            trace.append({"kind": "call", "name": c["name"], "detail": c["args"]})
        if m.type == "tool":
            trace.append({"kind": "result", "name": m.name, "detail": str(m.content)})

    return jsonify({"reply": result["messages"][-1].content, "trace": trace})


if __name__ == "__main__":
    print("도구:", TOOL_NAMES)
    print("→ http://localhost:5081")
    app.run(port=5081, debug=False)
