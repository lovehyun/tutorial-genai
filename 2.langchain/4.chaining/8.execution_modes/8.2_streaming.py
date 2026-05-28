"""
스트리밍 심화 — .stream() / .astream() / .astream_events()

  - .stream()         : 동기 토큰 스트림
  - .astream()        : 비동기 토큰 스트림 (FastAPI, aiohttp 등)
  - .astream_events() : 체인 내부 step 이벤트 추적 (디버깅)
"""

import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_template("{question}")
chain = prompt | llm | StrOutputParser()

question = "파이썬의 장점 3가지를 알려줘."


# (1) 동기 스트리밍
print("=" * 60)
print("(1) for chunk in chain.stream(...)")
print("=" * 60)
print(f"[질문] {question}\n[답변] ", end="", flush=True)
for chunk in chain.stream({"question": question}):
    print(chunk, end="", flush=True)
print()


# (2) 비동기 스트리밍
print("\n" + "=" * 60)
print("(2) async for chunk in chain.astream(...)")
print("=" * 60)

async def stream_async():
    print(f"[질문] {question}\n[답변] ", end="", flush=True)
    async for chunk in chain.astream({"question": question}):
        print(chunk, end="", flush=True)
    print()

asyncio.run(stream_async())


# (3) 체인 내부 이벤트 스트리밍
print("\n" + "=" * 60)
print("(3) astream_events — 체인 내부 step 추적")
print("=" * 60)

async def stream_events():
    interesting = {
        "on_chat_model_start", "on_chat_model_end",
        "on_parser_start", "on_parser_end",
        "on_chain_start", "on_chain_end",
    }
    async for event in chain.astream_events({"question": "안녕!"}, version="v2"):
        kind = event["event"]
        if kind in interesting:
            print(f"  {kind:25s} | name={event.get('name', '?')}")

asyncio.run(stream_events())
