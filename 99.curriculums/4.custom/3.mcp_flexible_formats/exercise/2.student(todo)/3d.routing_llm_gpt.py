"""
5c — GPT function calling 으로 '여러 MCP 서버'의 도구를 자동 선택·호출.
(3c.routing_manual = 키워드 규칙 / 여기 = LLM 자동)

TODO 2개: (1) MCP 도구 스키마를 OpenAI function 형식으로 변환해서 등록하기
          (2) GPT 가 고른 도구 이름으로 올바른 서버 세션을 찾아 실제로 호출하기
"""

import json
import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
gpt = AsyncOpenAI()
SERVERS = ["3a.math_server.py", "3b.utility_server.py"]


async def connect(server_file, stack):
    read, write = await stack.enter_async_context(
        stdio_client(StdioServerParameters(command="python", args=[server_file]))
    )
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session, (await session.list_tools()).tools


async def main():
    async with AsyncExitStack() as stack:
        oa_tools = []                 # OpenAI function 형식 도구 목록 (모든 서버 합본)
        tool_session = {}             # tool_name → 그 도구를 가진 세션 (실행 라우팅용)

        # 1) 서버들에 접속해서 사용 가능한 툴들 가져오기
        for sf in SERVERS:
            session, tools = await connect(sf, stack)
            for t in tools:
                # TODO 1: t(도구 정보)를 OpenAI function 스키마로 바꿔 oa_tools 에 추가하세요.
                #   힌트 — {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}
                #   t.name / t.description / t.inputSchema 를 그대로 쓰면 된다.
                #   그리고 tool_session[t.name] = session 도 잊지 말 것 (나중에 실행할 서버를 찾는 용도).
                pass  # ← 여기를 채우세요
        print("전체 도구:", list(tool_session))

        for q in ["안녕하세요 Alice!", "15 더하기 25는?", "지금 몇 시?", "부산 날씨는?", "파일 삭제해줘"]:
            # 2) 질문을 기반으로 툴 사용여부 결정
            print(f"\n질문: {q}")
            r = await gpt.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": q}],
                tools=oa_tools, tool_choice="auto",
            )
            msg = r.choices[0].message
            if not msg.tool_calls:                 # 적합한 도구 없음 → 바로 답
                print(f"답변: {msg.content}")
                continue

            call = msg.tool_calls[0]
            args = json.loads(call.function.arguments)
            print(f"  선택: {call.function.name}({args})  → 해당 서버 세션으로 실행")

            # TODO 2: GPT 가 고른 도구(call.function.name)를 '그 도구를 가진 서버 세션'으로 실행하세요.
            #   힌트 — tool_session 딕셔너리에서 이름으로 세션을 찾아 call_tool(이름, 인자) 호출.
            #   결과 텍스트는 result.content[0].text 에 들어있다.
            tool_result = None  # ← 여기를 채우세요
            print(f"답변: {tool_result}")

            # 4) 기존 질문 + GPT의 도구 호출 요청 + 실제 도구 결과를 다시 GPT에 전달하여 최종 답변 만들기
            final_r = await gpt.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": q},
                    msg,
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": tool_result,
                    },
                ],
            )

            print(f"답변: {final_r.choices[0].message.content}")


if __name__ == "__main__":
    asyncio.run(main())
