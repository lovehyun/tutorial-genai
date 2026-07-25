"""
Sampling 클라이언트 — 서버가 되묻는 sampling/createMessage 요청을 '내가' 처리한다.

핵심: ClientSession(read, write, sampling_callback=...) 로 콜백을 등록한다.
서버가 ctx.session.create_message(...) 를 호출하면 이 콜백이 실행된다.

여기서는 LLM 대신 '가짜 요약기'(첫 문장만 반환)를 넣어 흐름만 보여준다.
실제로는 이 콜백 안에서 OpenAI/Anthropic API 를 호출하면 된다(아래 메모 참고).

실행:  python client.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.context import RequestContext
from mcp.types import CreateMessageResult, CreateMessageRequestParams, TextContent

# Windows 콘솔(cp949)에서도 한글·특수문자 출력이 깨지거나 죽지 않게 UTF-8 로
sys.stdout.reconfigure(encoding="utf-8")


# ── 서버가 되묻는 sampling 요청을 처리하는 콜백 ──────────────────────
# 시그니처(mcp 1.13): async (context, params) -> CreateMessageResult | ErrorData
async def sampling_callback(
    context: RequestContext,
    params: CreateMessageRequestParams,
) -> CreateMessageResult:
    # 서버가 보낸 프롬프트
    prompt = params.messages[0].content.text
    print(f"[클라이언트] 서버가 생성 요청을 보냄:\n   {prompt!r}\n")

    # ── 여기가 진짜 LLM 을 호출할 자리 ──
    # 데모라서 '첫 문장만 뽑는 가짜 요약기' 로 대체한다.
    body = prompt.split("\n\n", 1)[-1]
    fake_summary = body.strip().split(".")[0].strip() + " (요약됨)"

    return CreateMessageResult(
        role="assistant",
        content=TextContent(type="text", text=fake_summary),
        model="fake-local-summarizer",   # 어떤 모델이 만들었는지 알림용
        stopReason="endTurn",
    )


async def main():
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        # ★ sampling_callback 을 등록해야 서버의 create_message 가 동작한다
        async with ClientSession(read, write, sampling_callback=sampling_callback) as session:
            await session.initialize()

            long_text = (
                "MCP 는 LLM 과 도구를 잇는 표준 프로토콜이다. "
                "서버를 한 번 만들면 어떤 클라이언트에서든 재사용할 수 있다. "
                "덕분에 도구 제공자와 사용처가 깔끔하게 분리된다."
            )
            result = await session.call_tool("summarize", {"text": long_text})
            print("[클라이언트] 도구 최종 결과:", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())

# 실제 LLM 을 붙이려면 sampling_callback 안을 이렇게 바꾼다:
#   from openai import OpenAI
#   client = OpenAI()
#   resp = client.chat.completions.create(model="gpt-4o-mini",
#            messages=[{"role": "user", "content": prompt}])
#   text = resp.choices[0].message.content
#   return CreateMessageResult(role="assistant",
#            content=TextContent(type="text", text=text),
#            model="gpt-4o-mini", stopReason="endTurn")
