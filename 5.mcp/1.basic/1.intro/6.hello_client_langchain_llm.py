"""
LLM 이 여러 MCP 도구 중 뭘 쓸지 스스로 고르게 하는 첫 예제.

지금까지(4.hello_client.py)는 우리가 직접 call_tool("hello", {...}) 를 호출했다(수동).
여기서는 langchain-mcp-adapters 가 MCP 도구(hello/get_date/get_time) → LangChain Tool 로
자동 변환하고, LLM 이 질문을 보고 "어떤 도구를 어떤 인자로" 부를지 스스로 결정한다(자동).

이 흐름을 프레임워크 없이 직접 손으로 짜본 걸 보고 싶다면 → ../2.protocol_deep (LLM 없이 수동 호출)
LangChain 도입 배경을 더 보고 싶다면 → ../../4.langchain/1.quickstart/1.agent.py (이 파일의 원형)

준비:
  pip install mcp langchain-mcp-adapters langchain-openai python-dotenv
  .env 에 OPENAI_API_KEY
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "5.hello_server.py")

# 도구가 있는 질문 셋(hello/date/time) + 도구가 없는 질문(날씨) 하나를 섞었다.
QUESTIONS = [
    "John 에게 인사해줘",
    "지금 날씨는?",
    "지금 날짜는?",
    "지금 시간은?",
]


async def main():
    # 1) 5.hello_server.py 를 자식 프로세스로 띄운다
    client = MultiServerMCPClient({
        "hello": {"command": "python", "args": [SERVER], "transport": "stdio"},
    })

    # 2) MCP 도구 → LangChain Tool 자동 변환
    tools = await client.get_tools()
    print(f"가져온 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    for question in QUESTIONS:
        print("=" * 50)
        print(f"[질문] {question}")

        result = await agent.ainvoke({"messages": [("user", question)]})

        # LLM 이 이번 질문에서 어떤 MCP 도구를 골랐는지(안 골랐으면 안 찍힘)
        called = False
        for m in result["messages"]:
            for c in (getattr(m, "tool_calls", None) or []):
                print(f"  → MCP 도구 호출: {c['name']}({c['args']})")
                called = True
        if not called:
            print("  → (도구 호출 없음 — 맞는 도구가 없어서 텍스트로만 답함)")

        print(f"[답변] {result['messages'][-1].content}\n")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - "날씨"는 서버에 없는 도구다 — LLM 이 hello/get_date/get_time 중 아무거나 억지로
#     불러 대충 지어내는지, 아니면 "그런 도구가 없다"고 솔직히 답하는지 실행해서 직접 확인해보자.
#   - 5.mcp/1.basic/1.intro/4.hello_client.py 와 비교해보면: 그건 도구 이름("hello")을 코드에 직접 박았고,
#     여기선 질문 문장만 주면 LLM 이 도구 이름과 인자(예: {"name": "John"})를 스스로 채운다.
