# app.py — 컨시어지 챗봇: 하나의 에이전트가 '쇼핑몰'과 '여행사' 두 MCP 서버를 동시에 쓴다.
#
# ── 핵심 아이디어 ────────────────────────────────────────────
#   사용자는 '내 사이트'에서 대화만 한다. 그러면 한 에이전트가 뒤에서
#   서로 다른 두 회사의 MCP 서버(쇼핑몰 / 여행사)에 동시에 붙어 일을 처리한다.
#     MultiServerMCPClient({쇼핑몰, 여행사}) → get_tools() 가 두 서버의 도구를 '한 묶음'으로 합침
#     create_agent(llm, tools) → 에이전트가 질문을 보고 어느 회사 도구를 쓸지 자동 라우팅
#   복합 요청("도쿄 여행 예약하고 캐리어도 사줘")이면 travel + shopping 도구를 순서대로 호출.
#
# 실행:  pip install flask langchain-openai langchain-mcp-adapters langgraph python-dotenv
#        OPENAI_API_KEY 설정 후  python app.py  → http://localhost:5060

import os
import asyncio
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()
HERE = os.path.dirname(os.path.abspath(__file__))

SYSTEM = (
    "너는 쇼핑·여행 컨시어지다. 두 외부 서비스의 도구를 쓸 수 있다:\n"
    "- 쇼핑몰: search_products / get_deal / place_order / list_orders\n"
    "- 여행사: search_trips / book_trip / list_bookings\n"
    "사용자 요청을 보고 알맞은 도구를 골라 처리하고, 복합 요청은 여러 도구를 순서대로 사용하라. "
    "'사줘/주문해줘/예약해줘' 면 검색에서 멈추지 말고 place_order / book_trip 까지 실제로 완료하라."
)


async def build_agent():
    """쇼핑몰·여행사 두 MCP 서버를 띄우고 도구를 한 묶음으로 받아 에이전트를 만든다."""
    client = MultiServerMCPClient({
        "shopping": {"command": "python", "args": [os.path.join(HERE, "shopping_server.py")], "transport": "stdio"},
        "travel":   {"command": "python", "args": [os.path.join(HERE, "travel_server.py")],   "transport": "stdio"},
    })
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return create_agent(llm, tools, system_prompt=SYSTEM), [t.name for t in tools]


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
    used = [c["name"] for m in result["messages"] for c in (getattr(m, "tool_calls", []) or [])]
    return jsonify({"reply": result["messages"][-1].content, "tools_used": used})


if __name__ == "__main__":
    print("도구:", TOOL_NAMES, "→ http://localhost:5060")
    app.run(port=5060, debug=False)
