"""
2.client_agent.py — 이미 떠 있는 '원격' MCP 서버에 LangChain 에이전트를 붙인다.

이 예제: 1.server_simple.py 를 HTTP 로 띄워두고, 그 도구들을 LLM 이 자동으로 골라 쓰게 한다.

1.quickstart/1.agent.py 와의 차이 — 딱 설정 딕셔너리 한 덩어리뿐:
    stdio : {"command": "python", "args": [SERVER], "transport": "stdio"}      ← 서버를 내가 띄움
    http  : {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable_http"} ← 이미 떠 있는 서버에 접속
  get_tools() 이후의 코드(도구 변환 → create_agent → ainvoke)는 완전히 동일하다.
  즉 "전송 방식은 에이전트 코드에 영향을 주지 않는다" 는 것이 이 단계의 관전 포인트.

준비:
  pip install mcp langchain langchain-openai langchain-mcp-adapters langgraph python-dotenv
  .env 에 OPENAI_API_KEY

실행:
  터미널 1)  python 1.server_simple.py     ← 먼저 서버를 띄워둔다
  터미널 2)  python 2.client_agent.py
"""

import asyncio

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

load_dotenv()

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    # ─── 원격 MCP 서버 등록 ────────────────────────────────────
    #   ⚠️ transport 리터럴이 서버 쪽과 다르다:
    #        서버   mcp.run(transport="streamable-http")   ← 하이픈
    #        클라   {"transport": "streamable_http"}       ← 언더스코어
    #      langchain-mcp-adapters 는 언더스코어만 인식한다.
    #
    #   ※ 1.basic/3.transports_http/client_http.py 처럼
    #        from mcp.client.streamable_http import streamable_http_client
    #     을 직접 import 하지 않는 이유:
    #     그 함수는 MultiServerMCPClient 가 내부에서 대신 호출해 준다.
    #     여기서 쓰는 "streamable_http" 문자열은 '그 함수를 쓰라' 고 알려주는 선택 스위치일 뿐이다.
    #        "stdio"           → 내부적으로 stdio_client(...) 호출 + 서버 프로세스 실행
    #        "streamable_http" → 내부적으로 streamable_http_client(url) 호출
    #     즉 저수준 함수를 직접 부르느냐(1.basic), 어댑터에 맡기느냐(여기) 의 차이다.
    client = MultiServerMCPClient({
        "toolbox": {
            "url": SERVER_URL,
            "transport": "streamable_http",
        },
    })


    # ─── MCP 도구 → LangChain Tool 자동 변환 (stdio 와 동일) ────
    try:
        tools = await client.get_tools()
    except Exception as e:
        print(f"[연결 실패] {SERVER_URL} 에 붙지 못했습니다: {type(e).__name__}: {e}")
        print("→ 다른 터미널에서 'python 1.server_simple.py' 를 먼저 실행했는지 확인하세요.")
        return

    print(f"원격 서버에서 가져온 도구 {len(tools)}개:", [t.name for t in tools], "\n")


    # ─── 에이전트 — 로컬 도구와 똑같이 사용 ────────────────────
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_agent(llm, tools)

    question = "17 더하기 25는 얼마야? 그리고 '원격 MCP 서버에 붙었다' 가 몇 단어인지도 세줘."
    print(f"[질문] {question}\n")

    result = await agent.ainvoke({"messages": [("user", question)]})

    # LLM 이 어떤 원격 도구를 호출했는지 추적
    for m in result["messages"]:
        if hasattr(m, "tool_calls") and m.tool_calls:
            for c in m.tool_calls:
                print(f"  → 원격 도구 호출: {c['name']}({c['args']})")

    print(f"\n[답변] {result['messages'][-1].content}")


if __name__ == "__main__":
    asyncio.run(main())


# 정리:
#   - 서버를 '내가 띄우는 자식 프로세스' 에서 '접속하는 원격 서비스' 로 바꿔도 에이전트 코드는 그대로.
#   - 덕분에 서버를 팀 공용으로 한 대 띄워두고 여러 클라이언트가 공유하는 구성이 가능해진다.
#   - 다음: 3.server_stock.py — 실제 외부 API 를 호출하는 '쓸모 있는' 원격 서버.
