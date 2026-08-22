# 2.client_manual_nlp.py — 규칙(정규식) 기반 '수동' 도구 선택 (LLM 없이)
#   사용자 문장을 정규식으로 분석해 어떤 MCP 도구를 부를지 직접 고른다.
#   다음 단계(3.client_gpt.py)에서 이 '선택'을 GPT 에게 맡긴다.
#   ※ 같은 걸 클래스로 구성한 버전: 2.client_simple_nlp_class.py

import asyncio
import re

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def select_tool(user_input):
    """사용자 입력을 규칙으로 분석해 (도구이름, 인자) 를 고른다. LLM 없이 손으로."""
    # 인사 패턴
    if any(word in user_input for word in ["안녕", "hello", "hi"]):
        m = re.search(r"([A-Z][a-z]+)", user_input)   # 대문자로 시작하는 영어 이름 추출
        name = m.group(1) if m else "None"
        return "hello", {"name": name}

    # 덧셈 패턴
    if any(word in user_input for word in ["더하기", "+", "덧셈"]):
        numbers = re.findall(r"\d+", user_input)        # 숫자 리스트 ['5', '3']
        if len(numbers) >= 2:
            return "add", {"a": int(numbers[0]), "b": int(numbers[1])}

    # 시간 패턴
    if any(word in user_input for word in ["시간", "몇 시", "지금"]):
        return "now", {}

    return None, {}


async def process_request(session, tool_names, user_input):
    """요청 하나 처리: 도구 선택 → 호출 → 결과 텍스트 반환."""
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


            # 서버가 제공하는 도구 이름들 (선택 검증용)
            tool_names = {t.name for t in (await session.list_tools()).tools}
            print(f"로드된 도구: {sorted(tool_names)}")

            print("\n" + "=" * 40)
            print("간단한 AI 에이전트 테스트 (규칙 기반)")
            print("=" * 40)

            test_cases = [
                "안녕하세요 Alice!",
                "안녕하세요 저는 홍길동 입니다.",
                "5 더하기 3은 얼마야?",
                "지금 몇 시야?",
                "이해할 수 없는 요청",
            ]

            for user_input in test_cases:
                response = await process_request(session, tool_names, user_input)
                print(f"AI: {response}")
                print("-" * 30)


if __name__ == "__main__":
    asyncio.run(main())
