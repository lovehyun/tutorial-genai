"""
MCP 5단계: 공식 외부 MCP 서버를 가져다 쓴다 (filesystem).
이 예제: 직접 만들지 않은 공식 filesystem MCP 서버를 띄우고, 파일을 읽는 에이전트.

내 서버(1.agent)와의 차이:
  - 코드(서버)를 우리가 작성하지 않는다 — 공식 서버를 npx 로 실행만 한다.
  - 1.agent 와 클라이언트 코드는 거의 동일하다. command 가 python → npx 로 바뀐 것뿐.
  - "한 번 만든 서버는 어디서든 재사용" 이라는 MCP 의 가치를 체감하는 단계.

준비:
  pip install langchain-mcp-adapters langchain-openai langgraph
  Node.js 18+ (공식 서버 다수가 Node 로 동작 → npx 필요)
  .env 에 OPENAI_API_KEY
"""

import asyncio
import os
import tempfile
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

load_dotenv()


async def main():
    # ─── 데모용 작업 디렉토리 + 파일 준비 ──────────────────────
    work_dir = tempfile.mkdtemp(prefix="mcp_demo_")
    sample_path = os.path.join(work_dir, "hello.txt")
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write("안녕하세요! MCP 데모 파일입니다.\n오늘 날짜: 2026-06-03")
    print(f"작업 디렉토리: {work_dir}")
    print(f"샘플 파일:    {sample_path}\n")

    # ─── 공식 filesystem 서버 (npx 로 실행) ───────────────────
    #   1.agent 의 {command:"python", args:[내 서버]} 와 형태가 같다.
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
        desc = (t.description or "(no desc)")[:80]
        print(f"  - {t.name}: {desc}...")
    print()

    # ─── 에이전트 — 일반 도구처럼 사용 ─────────────────────────
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = f"{work_dir} 디렉토리의 파일 목록을 보여주고, hello.txt 내용도 읽어줘."
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

# 정리:
#   - 공식 서버는 우리가 만들지 않아도 됨 (filesystem/github/postgres 등 수십 개).
#   - 같은 서버를 Claude Desktop / Cursor / LangChain 등에서 그대로 재사용.
#   - 공식 서버 모음: https://github.com/modelcontextprotocol/servers
