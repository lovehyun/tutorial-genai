"""
MCP 2단계: 순수 MCP 클라이언트로 내 서버에 붙어 본다 (LangChain 없음).
이 예제: 1.server_minimal 서버를 자식 프로세스로 띄우고, stdio 로 연결해
         도구 목록을 받아오고(list_tools) 도구를 호출한다(call_tool).

왜 LangChain 없이?
  - MCP 의 '날것' 흐름을 직접 보기 위해서다.
  - initialize → list_tools → call_tool 이 MCP 프로토콜의 핵심 3동작.
  - 이걸 보고 나면 4.langchain 의 langchain-mcp-adapters 가 "이 과정을 대신 해주는 것" 임을 안다.

준비:
  pip install mcp

흐름:
  1) StdioServerParameters 로 "python 1.server_minimal.py" 를 띄운다
  2) ClientSession 으로 핸드셰이크(initialize)
  3) list_tools() 로 서버가 제공하는 도구 명세 확인
  4) call_tool("add", {...}) 로 실제 호출 → 결과 수신
"""

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1.server_minimal.py 의 절대 경로 (이 파일 위치 기준)
HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "1.server_minimal.py")


async def main():
    # 1) 어떤 명령으로 서버를 띄울지 정의 — 파이썬으로 1.server_minimal 서버 실행
    server_params = StdioServerParameters(command="python", args=[SERVER])

    # 2) 서버를 자식 프로세스로 띄우고 stdio 파이프(read/write) 를 얻는다
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()              # 핸드셰이크

            # 3) 서버가 제공하는 도구 명세 조회
            tools = await session.list_tools()
            print("서버가 제공하는 도구:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # 4) 도구 실제 호출
            result = await session.call_tool("add", {"a": 3, "b": 5})
            # 결과는 content 블록 리스트로 온다(텍스트/이미지 등). 여기선 텍스트 1개.
            print("\nadd(3, 5) =", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())

# 정리:
#   - 서버(1.server_minimal)는 도구 제공 프로세스, 클라이언트(2.client_raw)는 그걸 호출하는 쪽.
#   - 여기까지가 MCP 의 '기본기' — LLM 도, 에이전트도 아직 등장하지 않았다.
#   - 4.langchain 부터 이 도구들을 LLM 에이전트가 자동으로 골라 쓰게 만든다.
