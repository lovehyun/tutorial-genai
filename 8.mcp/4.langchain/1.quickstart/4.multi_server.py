"""
MCP 7단계: 여러 MCP 서버를 한 클라이언트에 동시에 연결 (멀티 서버).
이 예제: 내가 만든 toolbox 서버(3.server_tools_resource) + 공식 filesystem 서버를 함께 띄우고,
         두 서버의 도구를 한 에이전트가 자유롭게 골라 쓰게 한다.

핵심:
  - MultiServerMCPClient 는 이름 → 서버설정 딕셔너리로 여러 서버를 한 번에 관리한다.
  - get_tools() 는 모든 서버의 도구를 하나의 리스트로 합쳐서 돌려준다.
  - "내 서버 + 공식 서버" 를 한 에이전트로 — 지금까지 단계의 종합.

준비:
  pip install mcp langchain-mcp-adapters langchain-openai langgraph
  Node.js (npx, filesystem 서버용) / .env 에 OPENAI_API_KEY
"""

import asyncio
import os
import tempfile
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLBOX = os.path.join(HERE, "..", "..", "1.common", "2.protocol_deep", "5.server_tools_resource.py")


async def main():
    # 데모 파일 준비
    work_dir = tempfile.mkdtemp(prefix="mcp_multi_")
    with open(os.path.join(work_dir, "memo.txt"), "w", encoding="utf-8") as f:
        f.write("멀티 서버 데모 메모 파일")

    # ─── 두 서버를 한 클라이언트에 등록 ────────────────────────
    client = MultiServerMCPClient({
        # (1) 내가 만든 파이썬 서버 — add / multiply / word_count
        "toolbox": {
            "command": "python",
            "args": [TOOLBOX],
            "transport": "stdio",
        },
        # (2) 공식 filesystem 서버 — 파일 읽기/쓰기
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", work_dir],
            "transport": "stdio",
        },
    })

    tools = await client.get_tools()   # 두 서버 도구가 한 리스트로 합쳐짐
    print(f"전체 도구 {len(tools)}개:", [t.name for t in tools], "\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    # filesystem(읽기) + toolbox(word_count) 가 한 질문에서 협력
    question = f"{work_dir} 의 memo.txt 를 읽고, 그 내용이 몇 단어인지 세줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구: {c['name']}({c['args']})")
    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

# 정리:
#   - 서버를 추가하고 싶으면 딕셔너리에 항목만 늘리면 된다(코드 구조는 그대로).
#   - 내 서버 + 공식 서버를 한 에이전트로 묶는 것이 실무 MCP 활용의 일반형.
