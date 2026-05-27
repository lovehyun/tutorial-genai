"""
스트리밍 심화 — .stream() / .astream() / .astream_events()

LLM 의 답변을 토큰 단위로 받아 챗봇처럼 글자가 흐르듯 보이게 한다.
세 가지 변형:
  - .stream()        : 동기 스트리밍
  - .astream()       : 비동기 스트리밍 (async/await 환경)
  - .astream_events(): 체인 내부 step 단위 이벤트 추적 (디버깅)
"""

import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    ("user",   "{question}"),
])
chain = prompt | llm | StrOutputParser()


# ============================================================
# (1) 동기 스트리밍 — 챗봇 UX 의 기본
# ============================================================
print("=" * 60)
print("(1) 동기 스트리밍 — for chunk in chain.stream(...)")
print("=" * 60)
question = "파이썬의 장점 3가지를 자세히 설명해줘."
print(f"[질문] {question}\n[답변] ", end="", flush=True)
for chunk in chain.stream({"question": question}):
    print(chunk, end="", flush=True)
print()


# ============================================================
# (2) 비동기 스트리밍 — async/await 환경 (FastAPI, aiohttp 등)
# ============================================================
print("\n" + "=" * 60)
print("(2) 비동기 스트리밍 — async for chunk in chain.astream(...)")
print("=" * 60)

async def stream_async():
    print(f"[질문] {question}\n[답변] ", end="", flush=True)
    async for chunk in chain.astream({"question": question}):
        print(chunk, end="", flush=True)
    print()

asyncio.run(stream_async())


# ============================================================
# (3) 이벤트 스트리밍 — 체인 내부 동작 추적 (디버깅용)
# ============================================================
# .astream_events() 는 체인의 각 step (prompt, llm, parser 등) 시작/종료를
# 이벤트로 받는다. 어떤 단계에서 시간이 오래 걸리는지, 어떤 step 이 실행됐는지
# 추적할 때 유용.
print("\n" + "=" * 60)
print("(3) astream_events — 체인 내부 step 이벤트 추적")
print("=" * 60)

async def stream_events():
    # 주요 이벤트만 필터링 (너무 많은 토큰 이벤트는 생략)
    interesting = {"on_chat_model_start", "on_chat_model_end",
                   "on_parser_start", "on_parser_end",
                   "on_chain_start", "on_chain_end"}
    async for event in chain.astream_events({"question": "안녕!"}, version="v2"):
        kind = event["event"]
        if kind in interesting:
            print(f"  {kind:25s} | name={event.get('name', '?')}")

asyncio.run(stream_events())

# 활용 팁:
#   - FastAPI 에서 챗봇 응답 streaming endpoint 만들 때 .astream() 사용
#   - LangSmith 등 trace 도구 없이 디버깅할 때 .astream_events() 가 가벼운 대안
