"""
codebase-QA 클라이언트 #1 — 순수 MCP 클라이언트 (LangChain 없음).
이 예제: server.py 를 띄우고 search / answer 도구를 직접 호출한다.

1.common/1.intro/4.hello_client.py 와 같은 패턴 — 서버만 'RAG 서버' 로 바뀐 것.

준비:
  pip install mcp langchain-openai langchain-community langchain-text-splitters python-dotenv
  .env 에 OPENAI_API_KEY
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = os.path.dirname(os.path.abspath(__file__))
# 기본은 자체 코퍼스 server.py. 실레포 문서 변형을 쓰려면:
#   QA_SERVER=server_docs.py python 1.client_raw.py
SERVER = os.path.join(HERE, os.getenv("QA_SERVER", "server.py"))


async def main():
    params = StdioServerParameters(command="python", args=[SERVER])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("도구:", [t.name for t in tools.tools], "\n")

            # 1) 검색만 (생성 없음)
            hits = await session.call_tool("search", {"query": "코사인 유사도", "k": 2})
            print("=== search('코사인 유사도') ===")
            print(hits.content[0].text, "\n")

            # 2) 완전한 RAG 답변
            ans = await session.call_tool(
                "answer", {"question": "MCP 에서 서버와 클라이언트의 차이는?"}
            )
            print("=== answer('MCP 서버 vs 클라이언트') ===")
            print(ans.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
