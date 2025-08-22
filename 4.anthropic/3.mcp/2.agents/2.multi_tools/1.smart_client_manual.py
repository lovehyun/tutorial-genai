import asyncio
from contextlib import AsyncExitStack
# async with 블록 안에서 만든 session을 리턴하고 있는데, 
# 함수가 끝나는 순간 컨텍스트가 종료되어 세션과 파이프가 닫힘.
# 그래서 이후 call_tool()은 항상 실패.
# 여러 서버 세션을 동시에 열고, main 루프가 끝날 때까지 유지하기 위해 AsyncExitStack 사용

import traceback  # 실패 시 오류 분석용

import re  # 인자갓 추출용

import asyncio
from contextlib import AsyncExitStack
# 여러 서버 세션을 동시에 열고, main 루프가 끝날 때까지 유지하기 위해 ExitStack 사용

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def get_tools_from_server(server_file, stack: AsyncExitStack):
    """
    특정 서버 실행 후 도구 목록을 가져오는 함수
    - AsyncExitStack에 세션을 등록하여, main() 끝날 때까지 세션이 유지되도록 함
    - 반환: (서버명, session, {tool_name: description})
    """
    params = StdioServerParameters(command="python", args=[server_file])

    # stdio_client → 서버 프로세스 실행 및 stdin/stdout 연결
    read, write = await stack.enter_async_context(stdio_client(params))

    # ClientSession → MCP 프로토콜 기반 세션 생성
    session = await stack.enter_async_context(ClientSession(read, write))
    await session.initialize()

    # 서버에서 제공하는 툴 목록 가져오기
    tools_result = await session.list_tools()
    tools = {t.name: t.description for t in tools_result.tools}

    return server_file, session, tools


def find_best_tool(question, all_tools):
    """
    사용자의 질문과 전체 도구 목록을 비교해 가장 적합한 도구 선택
    간단히 키워드 매칭으로 구현
    """
    q = question.lower()
    for tool_name, description in all_tools.items():
        if any(w in q for w in ["안녕", "hello"]) and "hello" in tool_name:
            return tool_name
        if any(w in q for w in ["더하기", "계산", "+"]) and "add" in tool_name:
            return tool_name
        if any(w in q for w in ["시간", "몇 시", "몇시"]) and "time" in tool_name:
            return tool_name
        if "날씨" in q and "weather" in tool_name:
            return tool_name
    return None


def extract_params(question, tool_name):
    """
    질문 텍스트에서 해당 도구에 필요한 파라미터 추출
    도구별 간단 규칙 기반
    """
    params = {}
    q = question.strip()

    if "hello" in tool_name:
        # 구두점 제거 후, 첫 번째 유효 단어를 name으로 사용
        tokens = re.findall(r"[A-Za-z가-힣]+", q)
        name = None
        for tok in tokens:
            if tok.lower() not in {"안녕하세요", "hello", "hi"}:
                name = tok
                break
        params["name"] = name or "친구"

    elif "add" in tool_name:
        # 숫자 2개 이상 뽑아서 a, b로 사용
        nums = re.findall(r"-?\d+(?:\.\d+)?", q)
        if len(nums) >= 2:
            params["a"] = float(nums[0])
            params["b"] = float(nums[1])

    elif "weather" in tool_name:
        # 질문에 포함된 도시명을 찾고 없으면 기본값 서울
        for city in ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]:
            if city in q:
                params["city"] = city
                break
        params.setdefault("city", "서울")

    return params


async def main():
    # 실행할 서버 목록
    servers = ["math_server.py", "utility_server.py"]

    # 처리할 질문 리스트
    questions = [
        "안녕하세요 Alice!",
        "5 더하기 7은?",
        "지금 몇 시야?",
        "서울 날씨는?",
        "파일 삭제해줘",
    ]

    # 여러 서버 세션을 동시에 관리하기 위해 ExitStack 사용
    async with AsyncExitStack() as stack:
        sessions = []     # (server_name, session, tools) 튜플 저장
        all_tools = {}    # 전체 도구 목록 합치기

        # 각 서버에 연결해서 도구 가져오기
        for server in servers:
            try:
                server_name, session, tools = await get_tools_from_server(server, stack)
                sessions.append((server_name, session, tools))

                # 서버별 도구 목록 출력
                print(f"{server_name}:")
                for name, desc in tools.items():
                    print(f"  - {name}: {desc}")

                # 전체 도구 사전에 병합
                all_tools.update(tools)
            except Exception:
                print(f"{server}: 연결 실패")
                traceback.print_exc()

        # 전체 도구 출력
        if all_tools:
            print("-" * 30)
            print("전체 도구:")
            for name, desc in all_tools.items():
                print(f"  - {name}: {desc}")
            print("-" * 30)
        else:
            print("등록된 도구가 없습니다.")
            return

        # 질문 처리 루프
        for q in questions:
            print(f"질문: {q}")
            tool_name = find_best_tool(q, all_tools)

            if not tool_name:
                print("답변: 적합한 도구 없음\n")
                continue

            # 질문에서 파라미터 추출
            params = extract_params(q, tool_name)

            executed = False
            # 모든 세션을 돌면서 해당 도구가 있는 서버에 호출 시도
            for server_name, session, tools in sessions:
                if tool_name not in tools:
                    continue
                try:
                    result = await session.call_tool(tool_name, params)
                    if hasattr(result, "content") and result.content:
                        content = result.content[0]
                        text = getattr(content, "text", None) or str(content)
                        print(f"답변: {text}")
                    else:
                        print("답변: (빈 응답)")
                    executed = True
                    break
                except Exception as e:
                    print(f"  - {server_name} 실행 실패: {e.__class__.__name__}: {e}")
                    # 필요하다면 traceback.print_exc()로 스택 출력

            if not executed:
                print("답변: 실행 실패")
            print()


if __name__ == "__main__":
    asyncio.run(main())
