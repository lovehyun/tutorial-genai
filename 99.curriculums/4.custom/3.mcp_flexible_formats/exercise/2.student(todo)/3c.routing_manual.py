"""
5b — 여러 MCP 서버 도구를 '키워드 규칙'으로 수동 선택 (LLM 없음).
5c(GPT 라우팅)의 '이전 단계' — 규칙 기반 선택이 얼마나 번거로운지 체감한다.

TODO: "날씨" 질문을 처리하는 규칙(find_tool)과 파라미터 추출(extract_params)을 완성하세요.
      hello/add/time 규칙은 이미 완성돼 있으니 패턴을 그대로 따라 하면 된다.
"""

import re
import asyncio
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVERS = ["3a.math_server.py", "3b.utility_server.py"]


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
        # TODO: "날씨" 키워드가 들어오면 weather 도구를 고르게 하세요.
        #   힌트 — 바로 위 시간 규칙과 같은 형태: if "날씨" in q and "weather" in name: return name
    return None


def extract_params(q, name):
    """질문에서 파라미터 추출 (수동 규칙)"""
    if "hello" in name:
        toks = [t for t in re.findall(r"[A-Za-z가-힣]+", q) if t.lower() not in {"안녕하세요", "hello", "hi"}]
        return {"name": toks[0] if toks else "친구"}
    if "add" in name:
        nums = re.findall(r"-?\d+", q)
        return {"a": int(nums[0]), "b": int(nums[1])} if len(nums) >= 2 else {}
    # TODO: weather 도구의 인자(city)를 문장에서 뽑아내세요.
    #   힌트 — 문장에 ["서울", "부산", "대구", "인천"] 중 하나가 들어있으면 그걸 city 로,
    #     없으면 기본값 "서울"을 쓴다.
    #     next((c for c in [...] if c in q), "서울") 형태를 참고.
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
