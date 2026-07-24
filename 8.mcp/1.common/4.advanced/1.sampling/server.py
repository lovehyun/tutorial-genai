"""
MCP 심화 (1) Sampling — 서버가 '거꾸로' 클라이언트의 LLM 에게 생성을 요청한다.

지금까지는 방향이 하나였다: 클라이언트 → 서버(도구 호출).
Sampling 은 그 반대다. 도구를 실행하던 서버가, 처리 도중 "이건 LLM 이 필요해" 라며
**클라이언트에게 되물어** 텍스트 생성을 시킨다. (서버는 API 키를 몰라도 된다 —
LLM 은 클라이언트 쪽에 있다.)

    클라이언트 ── call_tool("summarize") ──▶ 서버
    클라이언트 ◀── sampling/createMessage ── 서버   (도구 실행 도중, 역방향!)
    클라이언트 ── (자기 LLM 으로 생성) ─────▶ 서버
    클라이언트 ◀── 도구 결과 ───────────────── 서버

핵심 API:
    ctx.session.create_message(messages=[SamplingMessage(...)], max_tokens=...)
    → 클라이언트에 등록된 sampling_callback 이 호출되어 CreateMessageResult 를 돌려준다.

주의: 서버 도구가 sampling 을 쓰려면, 클라이언트가 반드시 sampling_callback 을
     등록하고 접속해야 한다(안 하면 "Sampling not supported" 에러).

준비:  pip install mcp
실행:  python client.py   (이 서버를 자식 프로세스로 띄운다)
"""

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import SamplingMessage, TextContent

mcp = FastMCP("sampling-demo")


@mcp.tool()
async def summarize(text: str, ctx: Context) -> str:
    """긴 글을 한 문장으로 요약한다. 요약 자체는 '클라이언트의 LLM' 에게 맡긴다."""
    # 서버는 직접 요약하지 않는다. 대신 클라이언트에게 "이 프롬프트로 생성해줘" 라고 되묻는다.
    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=f"다음 글을 딱 한 문장으로 요약해줘:\n\n{text}"),
            )
        ],
        max_tokens=200,
    )
    # result.content 는 클라이언트 LLM 이 생성한 응답
    summary = result.content.text if isinstance(result.content, TextContent) else str(result.content)
    return f"[요약] {summary}"


if __name__ == "__main__":
    mcp.run()

# 정리:
#   - 서버는 LLM 을 소유하지 않는다 → 어떤 클라이언트에 붙느냐에 따라 GPT/Claude 등이 바뀐다.
#   - '도구 실행 중' 에 모델 능력이 필요할 때 쓴다(요약·분류·재작성 등).
#   - 클라이언트가 sampling_callback 을 안 주면 이 도구는 실패한다 → client.py 참고.
