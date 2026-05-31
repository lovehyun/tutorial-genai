"""
MCP 클라이언트 — MCP 서버의 도구를 LangChain 에이전트로 가져와 사용.
이 예제: 공식 filesystem MCP 서버를 띄우고, 그 도구로 파일을 읽는 에이전트.

준비:
  pip install langchain-mcp-adapters langgraph langchain-openai

  # MCP 서버는 Node 로 실행 (공식 서버들 다수가 Node)
  npx --version          # Node.js 18+ 필요

흐름:
  1) MultiServerMCPClient 로 MCP 서버 시작 (stdio 통신)
  2) client.get_tools() 로 MCP 도구 → LangChain Tool 변환
  3) create_agent 에 그대로 넣어 사용

  ※ MultiServerMCPClient 는 비동기 — asyncio.run 으로 감싸야 합니다.
"""

import asyncio
import os
import tempfile
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent   # (구) langgraph.prebuilt.create_react_agent

load_dotenv()


async def main():
    # ─── 데모용 작업 디렉토리 + 파일 준비 ──────────────────────
    work_dir = tempfile.mkdtemp(prefix="mcp_demo_")
    sample_path = os.path.join(work_dir, "hello.txt")
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write("안녕하세요! MCP 데모 파일입니다.\n오늘 날짜: 2026-05-29")
    print(f"작업 디렉토리: {work_dir}")
    print(f"샘플 파일:    {sample_path}\n")


    # ─── MCP 클라이언트 — filesystem 서버 ──────────────────────
    client = MultiServerMCPClient({
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", work_dir],
            "transport": "stdio",
        },
    })


    # ─── MCP 도구 → LangChain Tool 자동 변환 ──────────────────
    tools = await client.get_tools()
    print(f"가져온 도구 수: {len(tools)}")
    for t in tools[:5]:
        print(f"  - {t.name}: {t.description[:80] if t.description else '(no desc)'}...")
    print()


    # ─── 에이전트 — 일반 LangChain 도구처럼 사용 ────────────────
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = f"{work_dir} 디렉토리에 있는 파일 목록 보여주고, hello.txt 내용도 읽어줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → MCP 도구: {c['name']}({c['args']})")
        if m.type == "tool":
            print(f"  ← 결과: {str(m.content)[:200]}...")

    print(f"\n[답변]\n{result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# ─────────────────────────────────────────────────────────
# 핵심:
#   - MCP 서버 자체는 우리가 만들지 않아도 됨 (공식 서버 다수)
#   - 같은 MCP 서버를 Claude Desktop / Cursor / LangChain 등에서 재사용
#   - 도구 명세 / 인증 / 보안이 MCP 표준으로 통일
#
# 더 보기:
#   - https://modelcontextprotocol.io/  (공식 문서)
#   - https://github.com/modelcontextprotocol/servers  (공식 서버 모음)
#   - 자체 MCP 서버 만들기는 mcp 파이썬 SDK 사용 (이 폴더 범위 밖)
# ─────────────────────────────────────────────────────────
