"""
mini-context7 클라이언트 #2 — LangChain 에이전트가 resolve_library_id → get_library_docs
2단계를 스스로 순서대로 호출한다 (도구 docstring 이 순서를 유도).

서버 자체는 키가 필요 없지만, 에이전트(LLM)는 필요하다 → 이 폴더에 .env (OPENAI_API_KEY).

준비:
  pip install mcp langchain-mcp-adapters langchain-openai langgraph python-dotenv
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")


async def main():
    client = MultiServerMCPClient({
        "mini-context7": {
            "command": "python",
            "args": [SERVER],
            "transport": "stdio",
        },
    })
    tools = await client.get_tools()
    print("가져온 도구:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = "FastAPI에서 쿼리 파라미터 받는 방법을 최신 문서 기준으로 알려줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
