# pip install claude-agent-sdk anyio
#
# 3단계: 커스텀 도구 — 내가 만든 함수를 에이전트가 호출하게 한다.
#
# `1.openai/7.function_calling`이나 `2.tools/1.tool_use.py`와 같은 개념(모델이 함수를
# 호출하도록 함)이지만, 여기서는 그 도구가 **MCP 서버 형태**로 등록된다는 게 다르다 —
# `@tool` + `create_sdk_mcp_server`로 만든 "내 프로세스 안에서 도는 MCP 서버"를 에이전트에 붙인다.
# (진짜 외부 MCP 서버를 붙이는 법은 `../../5.mcp/4.langchain/` 참고 — 여기는 그 축소판을
#  별도 프로세스 없이 코드 안에서 바로 만드는 방법이다.)
#
# 이번엔 query() 대신 ClaudeSDKClient를 쓴다 — 대화형 세션을 열고 닫는(async with) 방식.

import anyio
from claude_agent_sdk import (
    tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient,
    AssistantMessage, TextBlock, ResultMessage,
)


# [관전 포인트 1] @tool(이름, 설명, {인자명: 타입}) — 함수 하나가 곧 도구 하나.
@tool("get_weather", "특정 도시의 현재 날씨를 알려준다", {"city": str})
async def get_weather(args):
    city = args["city"]
    # 실전이라면 여기서 실제 날씨 API를 호출한다. 데모라 고정값을 돌려준다.
    return {"content": [{"type": "text", "text": f"{city}는 지금 맑고 22도입니다."}]}


# [관전 포인트 2] 도구를 모아 "내 프로세스 안에서 도는" MCP 서버로 패키징한다.
server = create_sdk_mcp_server(name="demo-tools", version="1.0.0", tools=[get_weather])

options = ClaudeAgentOptions(
    mcp_servers={"demo": server},
    # [관전 포인트 3] 도구 이름 규칙: mcp__<서버 이름>__<도구 이름>
    allowed_tools=["mcp__demo__get_weather"],
    tools=["mcp__demo__get_weather"],
    system_prompt="You are a concise assistant.",
    max_turns=3,
    max_budget_usd=0.1,
)


async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query("서울 날씨 어때?")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print("답변:", block.text)
            elif isinstance(message, ResultMessage):
                print(f"비용: ${message.total_cost_usd:.4f}")


anyio.run(main)
