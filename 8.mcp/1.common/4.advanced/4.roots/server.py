"""
MCP 심화 (4) Roots — 클라이언트가 서버에게 '작업 허용 경로' 를 알려준다.

Roots 는 클라이언트가 "너는 이 디렉토리들 안에서만 일해" 라고 서버에 알려주는 목록이다
(예: 열려 있는 워크스페이스 폴더). 서버는 ctx.session.list_roots() 로 그 목록을 물어본다.

    서버 ── roots/list ──▶ 클라이언트
    서버 ◀── [file:///..., ...] ── 클라이언트   (list_roots_callback 이 응답)

filesystem 류 서버가 "허용된 범위 밖 접근 거부" 를 구현할 때 쓴다.
Root 의 uri 는 반드시 file:// 로 시작한다(현행 스펙 제약).

준비:  pip install mcp
실행:  python client.py
"""

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP("roots-demo")


@mcp.tool()
async def show_roots(ctx: Context) -> str:
    """클라이언트가 허용한 작업 루트 목록을 조회해 돌려준다."""
    result = await ctx.session.list_roots()
    if not result.roots:
        return "허용된 root 가 없음 (클라이언트가 list_roots_callback 을 안 줬거나 빈 목록)"
    lines = [f"- {r.name or '(이름없음)'}: {r.uri}" for r in result.roots]
    return "허용된 작업 루트:\n" + "\n".join(lines)


@mcp.tool()
async def is_allowed(path: str, ctx: Context) -> str:
    """주어진 경로가 허용된 root 중 하나의 하위인지 검사한다(접근통제 예시)."""
    result = await ctx.session.list_roots()
    allowed_prefixes = [str(r.uri) for r in result.roots]     # 예: file:///workspace
    target = path if path.startswith("file://") else f"file://{path}"
    ok = any(target.startswith(pref) for pref in allowed_prefixes)
    return f"{'허용' if ok else '차단'}: {target}  (루트: {allowed_prefixes})"


if __name__ == "__main__":
    mcp.run()

# 정리:
#   - roots 는 '클라이언트가 서버에 주는 컨텍스트' — sampling/elicit 과 방향은 같지만 데이터.
#   - Root.uri 는 file:// 필수. 서버는 이를 화이트리스트로 삼아 접근을 제한할 수 있다.
