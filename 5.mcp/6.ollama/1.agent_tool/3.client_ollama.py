# pip install mcp ollama
#
# 3.client_ollama.py — 로컬 모델(Ollama)이 MCP 도구를 '자동' 선택·호출. API 키 불필요, 완전 무료·오프라인.
#
# 사전 준비:
#   1) https://ollama.com 에서 Ollama 설치(또는 앱 실행 — 로컬 서버가 자동으로 뜬다)
#   2) 모델 받기: ollama pull qwen2.5:7b   (도구 호출을 안정적으로 지원하는 범용 모델, 4.7GB)
#
# ── 연동 방식 ────────────────────────────────────────────────
#   1) session.list_tools() 로 MCP 도구 발견
#   2) 그 스키마(inputSchema)를 tools=[...] 형식으로 변환 — OpenAI function calling과 완전히
#      같은 모양이다(Ollama가 의도적으로 OpenAI 호환 포맷을 따른다). 그래서 2.openai/1.agent_tool/
#      3.client_gpt.py의 to_openai() 함수를 거의 그대로 재사용할 수 있다.
#   3) ollama.chat(tools=...) 에 넘기면 모델이 "어떤 도구를 어떤 인자로" 결정
#   4) 모델이 고른 도구를 session.call_tool() 로 MCP 실행
#   5) 실행 결과를 tool 메시지로 되돌려주면 모델이 자연스러운 문장으로 정리
#   (1.client_demo=수동 하드코딩, 2.client_manual_nlp=키워드, 여기=로컬 LLM 자동)

import asyncio

import ollama

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "qwen2.5:7b"


def to_ollama_tools(mcp_tools):
    """MCP 도구 스키마(inputSchema) → tools=[...] 형식. OpenAI function calling과 동일한 모양이다."""
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema,
    }} for t in mcp_tools]


async def ask(session, ol_tools, question):
    print(f"\n사용자: {question}")
    messages = [{"role": "user", "content": question}]

    # [관전 포인트 1] temperature=0 — 로컬 오픈웨이트 모델은 기본 temperature에서 도구 호출
    #   형식이 가끔 흔들린다(실제로 겪음: 구조화된 tool_calls 대신 텍스트로 새는 경우가 있었다).
    #   0으로 고정하니 반복 실행에서 안정적으로 재현됐다 — 상용 모델보다 이 설정이 더 중요하다.
    resp = ollama.chat(model=MODEL, messages=messages, tools=ol_tools, options={"temperature": 0})
    msg = resp.message

    if not msg.tool_calls:
        print(f"AI: {msg.content}")  # 도구 불필요 → 바로 답 (또는 맞는 도구가 없을 때)
        return

    # 2) 모델이 고른 도구를 MCP 로 실행
    call = msg.tool_calls[0]
    args = dict(call.function.arguments)
    print(f"  선택된 도구: {call.function.name}({args})")
    result = await session.call_tool(call.function.name, args)
    text = result.content[0].text

    # 3) 실행 결과를 모델이 자연스럽게 정리
    messages.append({
        "role": "assistant", "content": msg.content or "",
        "tool_calls": [{"function": {"name": call.function.name, "arguments": args}}],
    })
    messages.append({"role": "tool", "content": text})
    final = ollama.chat(model=MODEL, messages=messages, tools=ol_tools, options={"temperature": 0})
    print(f"AI: {final.message.content}")


async def main():
    params = StdioServerParameters(command="python", args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print("도구:", [t.name for t in tools])
            ol_tools = to_ollama_tools(tools)

            for q in ["5 더하기 3은 얼마야?", "지금 몇 시야?", "오늘 날씨는?"]:
                await ask(session, ol_tools, q)


if __name__ == "__main__":
    asyncio.run(main())


# ── 실행 결과 (실측, qwen2.5:7b) ─────────────────────────────
#   사용자: 5 더하기 3은 얼마야?
#     선택된 도구: add({'a': 5, 'b': 3})
#   AI: 5 더하기 3은 8입니다!
#
#   사용자: 지금 몇 시야?
#     선택된 도구: now({})
#   AI: 현재 시간은 2026년 8월 24일 오전 12시 20분 46초입니다.
#
#   사용자: 오늘 날씨는?          ← 맞는 도구가 없는 경우
#   AI: 현재 날씨 정보를 제공하지만, 날씨 관련 도구가 포함되어 있지 않습니다 ...
#   (⚠️ GPT-4o-mini/Claude보다 답이 덜 깔끔하다 — "관전 포인트" 참고)
