# 2.client_manual_nlp.py — 규칙(정규식) 기반 '수동' 도구 선택 (LLM 없이)
#
# 2.openai/1.agent_tool/2.client_manual_nlp.py, 3.anthropic/2.anthropic_api/2.client_manual_nlp.py
# 와 코드가 100% 동일하다. 다음 단계(3.client_ollama.py)에서 이 '선택'을 로컬 모델에게 맡긴다.

import asyncio
import re

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def select_tool(user_input):
    if any(word in user_input for word in ["안녕", "hello", "hi"]):
        m = re.search(r"([A-Z][a-z]+)", user_input)
        name = m.group(1) if m else "None"
        return "hello", {"name": name}

    if any(word in user_input for word in ["더하기", "+", "덧셈"]):
        numbers = re.findall(r"\d+", user_input)
        if len(numbers) >= 2:
            return "add", {"a": int(numbers[0]), "b": int(numbers[1])}

    if any(word in user_input for word in ["시간", "몇 시", "지금"]):
        return "now", {}

    return None, {}


async def process_request(session, tool_names, user_input):
    print(f"\n사용자: {user_input}")

    tool_name, params = select_tool(user_input)
    if not tool_name or tool_name not in tool_names:
        return "요청을 이해하지 못했습니다."

    print(f"선택된 도구: {tool_name}, 매개변수: {params}")
    result = await session.call_tool(tool_name, params) if params else await session.call_tool(tool_name)
    return result.content[0].text


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tool_names = {t.name for t in (await session.list_tools()).tools}
            print(f"로드된 도구: {sorted(tool_names)}")

            test_cases = [
                "안녕하세요 Alice!",
                "5 더하기 3은 얼마야?",
                "지금 몇 시야?",
                "이해할 수 없는 요청",
            ]
            for user_input in test_cases:
                response = await process_request(session, tool_names, user_input)
                print(f"AI: {response}")


if __name__ == "__main__":
    asyncio.run(main())
