# 1.smart_client_manual.py — 여러 MCP 서버 도구를 '키워드 규칙'으로 수동 선택 (LLM 없음)
# GPT 버전(2.smart_client_gpt) 의 '이전 단계' — 규칙 기반 선택이 얼마나 번거로운지 체감한다.
# AsyncExitStack 으로 여러 서버 세션을 main 끝까지 동시에 유지.

import re
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVERS = ["math_server.py", "utility_server.py"]


async def connect(server_file, stack):
    read, write = await stack.enter_async_context(
        stdio_client(StdioServerParameters(command="python", args=[server_file])))
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()
    return session, (await session.list_tools()).tools


def find_tool(q, tool_names):
    """키워드 매칭으로 도구 선택 (수동 규칙 — LLM 이라면 알아서 할 일)"""
    q = q.lower()
    for name in tool_names:
        if any(w in q for w in ["안녕", "hello"]) and "hello" in name: return name
        if any(w in q for w in ["더하기", "계산", "+"]) and "add" in name: return name
        if any(w in q for w in ["시간", "몇 시", "몇시"]) and "time" in name: return name
        if "날씨" in q and "weather" in name: return name
    return None


def extract_params(q, name):
    """질문에서 파라미터 추출 (수동 규칙)"""
    if "hello" in name:
        toks = [t for t in re.findall(r"[A-Za-z가-힣]+", q) if t.lower() not in {"안녕하세요", "hello", "hi"}]
        return {"name": toks[0] if toks else "친구"}
    if "add" in name:
        nums = re.findall(r"-?\d+", q)
        return {"a": int(nums[0]), "b": int(nums[1])} if len(nums) >= 2 else {}
    if "weather" in name:
        return {"city": next((c for c in ["서울", "부산", "대구", "인천"] if c in q), "서울")}
    return {}


async def main():
    async with AsyncExitStack() as stack:
        tool_session = {}                       # tool_name → 그 도구를 가진 세션
        for sf in SERVERS:
            session, tools = await connect(sf, stack)
            for t in tools:
                tool_session[t.name] = session
        print("전체 도구:", list(tool_session))

        for q in ["안녕하세요 Alice!", "5 더하기 7은?", "지금 몇 시야?", "서울 날씨는?", "파일 삭제해줘"]:
            print(f"\n질문: {q}")
            name = find_tool(q, tool_session)
            if not name:
                print("답변: 적합한 도구 없음 (규칙에 안 걸림)")
                continue
            params = extract_params(q, name)
            print(f"  선택(규칙): {name}({params})")
            result = await tool_session[name].call_tool(name, params)
            print(f"답변: {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())

# ── 실행 결과 (예) ───────────────────────────────────────────
#   전체 도구: ['hello', 'add', 'current_time', 'weather']
#   질문: 5 더하기 7은?
#     선택(규칙): add({'a': 5, 'b': 7})     ← find_tool 키워드매칭 + extract_params 정규식
#   답변: 5 + 7 = 12
#   질문: 파일 삭제해줘
#     답변: 적합한 도구 없음 (규칙에 안 걸림)
#   → 규칙 기반은 "5 더하기 7" 같은 정형 문장만 처리. 자유로운 표현은 3.client_gpt(LLM)이 강하다.
