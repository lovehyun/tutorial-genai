"""
codebase-QA 클라이언트 #2 — LangChain 에이전트가 RAG 서버를 도구로 사용.
이 예제: server.py 의 search / answer 를 LangChain 도구로 자동 변환해 에이전트에 붙인다.
        LLM 이 질문을 보고 'search 로 근거를 찾을지, answer 로 바로 답할지' 스스로 결정한다.

1.client_raw.py(수동 호출)와 비교 — 여기선 에이전트가 도구 선택을 자동으로 한다.

준비:
  pip install mcp langchain-mcp-adapters langchain-openai langchain-community langchain-text-splitters langgraph python-dotenv
  .env 에 OPENAI_API_KEY
"""

import asyncio
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
# 기본은 자체 코퍼스 server.py. 실레포 문서 변형을 쓰려면:
#   QA_SERVER=server_docs.py python 2.client_langchain.py
SERVER = os.path.join(HERE, os.getenv("QA_SERVER", "server.py"))


async def main():
    # RAG 서버를 stdio 로 띄워 도구를 가져온다
    client = MultiServerMCPClient({
        "codebase-qa": {
            "command": "python",
            "args": [SERVER],
            "transport": "stdio",
        },
    })
    tools = await client.get_tools()
    print("가져온 도구:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = "RAG 가 할루시네이션을 줄이는 원리를 코퍼스 근거로 설명해줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구 호출: {c['name']}({c['args']})")
    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())
