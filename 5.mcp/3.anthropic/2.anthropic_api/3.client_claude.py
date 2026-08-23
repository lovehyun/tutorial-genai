# pip install mcp anthropic python-dotenv
#
# 3.client_claude.py — Claude(Anthropic API, tool_use)가 MCP 도구를 '자동' 선택·호출
#
# ── 연동 방식 ────────────────────────────────────────────────
#   1) session.list_tools() 로 MCP 도구 발견
#   2) 그 스키마(inputSchema, camelCase)를 Anthropic tool_use 형식(input_schema, snake_case)으로 변환
#   3) Claude 에 tools=... 로 넘기면 stop_reason == "tool_use" 일 때 Claude 가 도구/인자를 결정
#   4) Claude 가 고른 도구를 session.call_tool() 로 MCP 실행
#   5) 실행 결과를 tool_result 로 되돌려주면 Claude 가 자연스러운 문장으로 정리
#   (1.client_demo=수동 하드코딩, 2.client_manual_nlp=키워드, 여기=LLM 자동)
#
# 2.openai/1.agent_tool/3.client_gpt.py 와 나란히 비교해서 볼 것 — 서버(server.py)는 완전히
# 같고, 스키마 변환 함수와 tool_use 프로토콜 처리 부분만 벤더별로 다르다.

import asyncio
import os

import anthropic
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def to_anthropic(tools):
    """MCP 도구 스키마(inputSchema) → Anthropic tool_use 형식(input_schema)."""
    return [{"name": t.name, "description": t.description, "input_schema": t.inputSchema} for t in tools]


async def ask(session, an_tools, user_input):
    print(f"\n사용자: {user_input}")
    messages = [{"role": "user", "content": user_input}]

    # 1) Claude 가 도구를 고르게 한다
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)

    if resp.stop_reason != "tool_use":
        print(f"AI: {next(b.text for b in resp.content if b.type == 'text')}")  # 도구 불필요 → 바로 답
        return

    # 2) Claude 가 고른 도구를 MCP 로 실행
    messages.append({"role": "assistant", "content": resp.content})
    tool_results = []
    for block in resp.content:
        if block.type == "tool_use":
            print(f"  선택된 도구: {block.name}({block.input})")
            result = await session.call_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result", "tool_use_id": block.id, "content": result.content[0].text,
            })
    messages.append({"role": "user", "content": tool_results})

    # 3) 도구 결과를 받은 뒤 최종 답변 (tool_result 로 되돌려줌 — 정석 패턴)
    final = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=500, tools=an_tools, messages=messages)
    print(f"AI: {next(b.text for b in final.content if b.type == 'text')}")


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])
            an_tools = to_anthropic(tools)

            for q in ["Claude 라고 인사해줘", "5 더하기 3은?", "지금 몇 시야?", "오늘 날씨는?"]:
                await ask(session, an_tools, q)


if __name__ == "__main__":
    asyncio.run(main())


# ── 실행 결과 (예) ───────────────────────────────────────────
#   도구: ['hello', 'add', 'now']
#
#   사용자: 5 더하기 3은?
#     선택된 도구: add({'a': 5, 'b': 3})
#   AI: 5 더하기 3은 8입니다.
#
#   사용자: 오늘 날씨는?          ← 맞는 도구가 없으면 Claude 가 도구 없이 바로 답
#   AI: 죄송하지만 현재 날씨 정보를 제공할 도구가 없어서 알려드릴 수 없습니다 ...
