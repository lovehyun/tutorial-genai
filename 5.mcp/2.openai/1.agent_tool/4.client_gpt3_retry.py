# pip install mcp openai python-dotenv
#
# 인자가 틀리면 GPT가 스스로 고쳐서 재시도한다 — 3.client_gpt.py는 도구 호출 → 결과 정리로 끝나는
# '한 번짜리' 왕복이었다. 실전에서는 첫 시도가 자주 틀린다(특히 서버 고유의 코드/포맷처럼 모델이
# 미리 알 수 없는 값). 이 파일은 반복문(루프)으로 "호출 → 실패 → 에러 메시지를 보고 → 재호출"이
# 여러 턴에 걸쳐 이어지는 걸 직접 확인한다.
#
# 핵심 설계: server2.py 의 도구는 실패해도 예외(raise)를 던지지 않고 "왜 틀렸는지 + 뭘 써야
# 하는지"를 텍스트로 돌려준다(2.protocol_deep/9~10 의 isError 패턴과 같은 발상). 그 텍스트가
# tool 메시지로 GPT 에게 그대로 전달되기 때문에, GPT 는 다음 턴에 그걸 읽고 스스로 고친다 —
# 우리가 "재시도 로직"을 따로 짤 필요가 없다. 도구 설계(에러를 어떻게 알려주는가)가 곧 재시도
# 능력을 결정한다는 게 이 예제의 요점이다.

import asyncio
import json

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
client = AsyncOpenAI()

MAX_TURNS = 5  # 무한 루프 방지 — 계속 틀리면 여기서 포기한다


def to_openai(tools):
    return [{"type": "function", "function": {
        "name": t.name, "description": t.description, "parameters": t.inputSchema}} for t in tools]


async def run(session, oa_tools, question):
    print(f"\n사용자: {question}")
    messages = [{"role": "user", "content": question}]

    for turn in range(1, MAX_TURNS + 1):
        r = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=oa_tools,
            tool_choice="auto",
            temperature=0,  # 재현성 — 이 데모는 "같은 실수를 하고 같은 방식으로 고치는" 걸 보여줘야 한다
            # [관전 포인트 1] 한 턴에 도구 호출을 하나씩만 하게 강제한다 — 여러 개를 한꺼번에
            #   부르면(parallel tool calls) 로그가 뒤섞여서 "실패→재시도" 흐름이 잘 안 보인다.
            parallel_tool_calls=False,
        )
        msg = r.choices[0].message
        if not msg.tool_calls:
            print(f"AI (최종, {turn}턴 만에): {msg.content}")
            return

        # [관전 포인트 2] assistant 메시지(도구 호출 포함)를 먼저 기록에 추가해야 한다 — 안 그러면
        #   다음 API 호출이 "tool_call에 대한 응답이 안 왔다"는 400 에러를 낸다(실제로 겪은 버그).
        messages.append(msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            print(f"  [turn {turn}] 도구 호출: {call.function.name}({args})")

            result = await session.call_tool(call.function.name, args)
            text = result.content[0].text
            print(f"  [turn {turn}] 결과: {text}")

            # [관전 포인트 3] 실패든 성공이든 그냥 tool 메시지로 돌려준다 — GPT 가 "실패했다"를
            #   판단하는 게 아니라 "결과 텍스트를 읽고" 다음 행동을 정한다.
            messages.append({"role": "tool", "tool_call_id": call.id, "content": text})

    print(f"AI: {MAX_TURNS}턴 안에 성공하지 못했습니다 — 사람이 개입할 시점.")


async def main():
    params = StdioServerParameters(command="python", args=["server2.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            oa_tools = to_openai(tools)

            # [관전 포인트 4] "결제 관련 급한 문제"라고만 말했지, 사내 코드(URG1/FIN-BILL 같은)는
            #   어디에도 안 알려줬다 — GPT가 알 방법이 없으니 그럴듯한 값(P1, PAY 등)으로 첫 시도를
            #   하고, 에러 메시지가 알려주는 진짜 코드로 다음 턴에 고쳐 부른다.
            await run(session, oa_tools,
                      "결제 관련해서 급한 문제가 생겼어, 지원 티켓 바로 만들어줘. "
                      "카드가 중복 결제됐어. 되는 값으로 알아서 시도해봐.")


if __name__ == "__main__":
    asyncio.run(main())


# ── 실행 결과 (실측) ─────────────────────────────────────────────
#   사용자: 결제 관련해서 급한 문제가 생겼어, 지원 티켓 만들어줘. 카드가 중복 결제됐어.
#     [turn 1] 도구 호출: create_support_ticket({'priority': 'P1', 'category': 'PAY', ...})
#     [turn 1] 결과: 티켓 생성 실패:
#       priority='P1'는 잘못된 코드입니다. 사용 가능한 코드: {'URG1': ..., 'URG2': ..., ...}
#       category='PAY'는 잘못된 코드입니다. 사용 가능한 코드: {'FIN-BILL': ..., 'TECH-BUG': ..., ...}
#     [turn 2] 도구 호출: create_support_ticket({'priority': 'URG1', 'category': 'FIN-BILL', ...})
#     [turn 2] 결과: 티켓 생성됨: [URG1/FIN-BILL] 카드 중복 결제 문제 발생
#   AI (최종, 2턴 만에): 지원 티켓이 성공적으로 생성되었습니다 ...
