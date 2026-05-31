"""
Flask 서버 점검 에이전트 — 현행 API 로 재작성한 풀스택 데모.
이 예제: 자연어 명령 → 적절한 점검 도구 자동 호출 → 결과 답변. + 멀티턴 메모리.

옛 scanapp.py (deprecated initialize_agent, Tool(query: str), 415줄) →
현행 (create_agent + @tool + MemorySaver, ~80줄 + 모듈화된 tools.py)

UI:
  GET  /          : 명령 입력 페이지
  POST /chat      : 점검 요청 (JSON {message, thread_id?})
                   → {answer, tools_used}
"""

import os
import uuid
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent   # (구) langgraph.prebuilt.create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import ALL_TOOLS

load_dotenv()


# ─── 에이전트 ──────────────────────────────────────────────
system_prompt = """\
당신은 서버 상태 점검을 도와주는 한국어 어시스턴트입니다.
- 자연어 요청을 적절한 점검 도구로 변환해 호출하세요.
- 결과는 한국어로 간결히 정리해 보여주세요.
- 임의 host/port 같은 인자는 사용자가 명시한 값을 그대로 사용.
- 한 번에 여러 점검이 필요하면 도구를 여러 번 호출하세요.
"""

checkpointer = MemorySaver()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(llm, ALL_TOOLS, system_prompt=system_prompt, checkpointer=checkpointer)


# ─── Flask ─────────────────────────────────────────────────
app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "").strip()
    if not message:
        return jsonify({"error": "메시지가 없습니다"}), 400

    # thread_id 없으면 신규 생성 → 응답에 같이 보내서 클라이언트가 후속 호출에 사용
    thread_id = body.get("thread_id") or str(uuid.uuid4())[:8]

    result = agent.invoke(
        {"messages": [("user", message)]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 15},
    )

    used = [
        c["name"] for m in result["messages"]
        if hasattr(m, "tool_calls") and m.tool_calls
        for c in m.tool_calls
    ]
    return jsonify({
        "answer":    result["messages"][-1].content,
        "tools_used": used,
        "thread_id": thread_id,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
