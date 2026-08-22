"""
MCP 심화 (3) Elicitation — 도구 실행 도중 '사용자에게 되묻기'.

위험하거나(삭제 등) 정보가 부족한 작업에서, 서버는 도구 실행을 멈추고
클라이언트(=사용자)에게 확인이나 추가 입력을 요청할 수 있다.

    ctx.elicit(message="정말 지울까요?", schema=ConfirmDelete)
      → 클라이언트의 elicitation_callback 이 뜨고, 사용자가 응답을 채운다.
      → 결과 action: "accept"(승인) / "decline"(거절) / "cancel"(그냥 닫음)

schema 는 pydantic BaseModel 로, **원시 타입(str/int/float/bool)만** 허용된다(스펙 제약).

sampling 과의 차이:
  - sampling  = 서버가 '클라이언트의 LLM' 에게 되물음(기계).
  - elicit    = 서버가 '사용자(사람)' 에게 되물음(확인/입력).

준비:  pip install mcp
실행:  python client.py
"""

from pydantic import BaseModel, Field

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("elicit-demo")


# 되물을 때 사용자가 채울 폼(원시 타입만!)
class ConfirmDelete(BaseModel):
    confirm: bool = Field(description="정말 삭제하려면 true")
    reason: str = Field(default="", description="삭제 사유(선택)")


@mcp.tool()
async def delete_file(path: str, ctx: Context) -> str:
    """파일을 삭제한다 — 단, 실제 삭제 전에 사용자 확인을 받는다(데모라 흉내만)."""
    result = await ctx.elicit(
        message=f"'{path}' 를 삭제할까요? 되돌릴 수 없습니다.",
        schema=ConfirmDelete,
    )

    # result 는 AcceptedElicitation / DeclinedElicitation / CancelledElicitation 중 하나
    if result.action == "accept" and result.data.confirm:
        note = f" (사유: {result.data.reason})" if result.data.reason else ""
        return f"[삭제됨] '{path}'{note}"          # 데모라 실제로 지우진 않음
    if result.action == "accept":                  # 폼은 냈지만 confirm=false
        return f"보류 — '{path}' 는 그대로 둠(확인란 미체크)"
    if result.action == "decline":
        return f"거절됨 — '{path}' 유지"
    return f"취소됨 — '{path}' 유지"                # cancel


if __name__ == "__main__":
    mcp.run()

# 정리:
#   - schema 필드는 반드시 원시 타입. 중첩 객체/리스트는 스펙상 불가.
#   - 클라이언트가 elicitation_callback 을 안 주면 "Elicitation not supported" 에러.
#   - action 세 가지(accept/decline/cancel)를 모두 처리하는 게 안전하다.
