# pip install mcp
#
# 리소스 템플릿(Resource Template) — 지금까지 resource는 전부 "info://server"처럼 고정 URI였다.
# 실전에서는 "이 파일을 읽어줘", "이 사용자 정보를 줘"처럼 URI에 값을 끼워 넣어야 한다 —
# @mcp.resource()에 {변수} 를 쓰면 URI 자체가 파라미터를 받는 템플릿이 된다.

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("resource-template-demo")


# [관전 포인트 1] URI 안의 {name} 이 함수 인자 name 과 매칭된다 — FastMCP 가 자동으로 파싱해서 넘겨준다.
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """이름을 받아 인사말을 돌려주는 템플릿 리소스."""
    return f"Hello, {name}! 반가워요."


# [관전 포인트 2] 변수 여러 개도 가능하다 — URI 경로 세그먼트 하나당 변수 하나.
@mcp.resource("user://{user_id}/profile/{field}")
def get_user_field(user_id: str, field: str) -> str:
    """가짜 사용자 DB에서 필드 하나를 조회하는 템플릿 리소스(데모용 하드코딩)."""
    fake_db = {
        "1": {"name": "Alice", "role": "admin"},
        "2": {"name": "Bob", "role": "viewer"},
    }
    user = fake_db.get(user_id)
    if user is None:
        return f"user_id={user_id} 없음"
    return str(user.get(field, f"field={field} 없음"))


if __name__ == "__main__":
    mcp.run(transport="stdio")
