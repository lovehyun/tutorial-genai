"""
MCP + 로컬 도구 혼합 — 외부(MCP) 도구와 내 @tool 을 한 에이전트에 함께.
이 예제: filesystem MCP 도구 + 로컬 계산 도구(word_count) 를 같이 등록.
실무에선 "외부 표준 도구(MCP) + 우리 도메인 도구(@tool)" 를 섞는 게 일반적입니다.

준비: pip install langchain-mcp-adapters  /  Node.js (npx) 필요
"""

import asyncio
import os
import tempfile
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()


# ─── 로컬 도구 — 우리 도메인 함수 ──────────────────────────
@tool
def word_count(text: str) -> int:
    """주어진 문자열의 단어 개수를 센다."""
    return len(text.split())


async def main():
    # 데모 파일 준비
    work_dir = tempfile.mkdtemp(prefix="mcp_local_")
    with open(os.path.join(work_dir, "note.txt"), "w", encoding="utf-8") as f:
        f.write("MCP 와 로컬 도구를 함께 쓰는 예제 입니다")

    # ─── MCP filesystem 서버의 도구 가져오기 ──────────────────
    client = MultiServerMCPClient({
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", work_dir],
            "transport": "stdio",
        },
    })
    mcp_tools = await client.get_tools()

    # ─── MCP 도구 + 로컬 @tool 을 한 번에 등록 ────────────────
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, mcp_tools + [word_count])   # ← 혼합이 핵심
    print(f"등록된 도구: MCP {len(mcp_tools)}개 + 로컬 1개(word_count)\n")

    # 파일 읽기(MCP) → 단어 수 세기(로컬) 를 한 흐름에서
    question = f"{work_dir} 의 note.txt 를 읽고, 그 내용이 몇 단어인지 세줘."
    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 도구: {c['name']}({c['args']})")
    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())

# 정리:
#   - mcp_tools + [내 @tool] 처럼 리스트만 합치면 끝 (둘 다 같은 BaseTool 인터페이스)
#   - 외부 표준(MCP) 과 내부 도메인 도구(@tool) 를 자연스럽게 한 에이전트로
