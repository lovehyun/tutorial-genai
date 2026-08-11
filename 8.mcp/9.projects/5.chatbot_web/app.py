# app.py — 웹 챗봇: LangChain 에이전트가 'MCP 서버의 도구'를 자동으로 써서 답한다.
#
# ── 연동 방식 ────────────────────────────────────────────────
#   1) MultiServerMCPClient 로 server.py 를 띄우고 get_tools() 로 MCP 도구 → LangChain 도구 변환
#   2) create_agent(llm, tools) — 에이전트가 사용자의 자연어를 보고 어떤 도구를 부를지 자동 결정
#   3) Flask /chat 엔드포인트가 메시지를 받아 agent.ainvoke → 답변 + '사용한 도구'를 반환
#   → 브라우저 채팅창에서 "12*7?", "지금 몇시?", "주사위 굴려줘", "서울 날씨" 등을 물어본다.
#
# 실행:  pip install flask langchain-openai langchain-mcp-adapters langgraph python-dotenv
#        OPENAI_API_KEY 설정 후  python app.py  → http://localhost:5050

import os
import asyncio
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()
HERE = os.path.dirname(os.path.abspath(__file__))


async def build_agent():
    """MCP 서버의 도구를 가져와 에이전트를 만든다 (서버 시작 시 1회)."""
    client = MultiServerMCPClient({
        "tools": {
            "command": "python",
            "args": [os.path.join(HERE, "server.py")],
            "transport": "stdio",
        }
    })
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_agent(llm, tools), [t.name for t in tools]


agent, TOOL_NAMES = asyncio.run(build_agent())
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", tools=", ".join(TOOL_NAMES))


@app.route("/chat", methods=["POST"])
def chat():
    message = (request.json or {}).get("message", "").strip()
    if not message:
        return jsonify({"reply": "메시지를 입력하세요.", "tools_used": []})
    result = asyncio.run(agent.ainvoke({"messages": [("user", message)]}))
    # 에이전트가 어떤 MCP 도구를 호출했는지 추적
    used = [c["name"] for m in result["messages"] for c in (getattr(m, "tool_calls", []) or [])]
    return jsonify({"reply": result["messages"][-1].content, "tools_used": used})


if __name__ == "__main__":
    print("도구:", TOOL_NAMES, "→ http://localhost:5050")
    app.run(port=5050, debug=False)
