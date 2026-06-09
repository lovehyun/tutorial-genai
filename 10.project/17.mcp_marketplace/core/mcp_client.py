"""
업스트림 MCP 서버와 통신하는 얇은 클라이언트 헬퍼.

두 군데서 쓴다:
  · app.py(등록/헬스)  : probe_tools — 서버에 붙어 도구 목록(inputSchema 포함)을 수집
  · gateway.py(프록시) : call_upstream — 컨슈머 호출을 실제 서버로 중계

모두 streamable-http 전송. 매 호출마다 새 세션을 연다(상태 없음=프록시에 적합).
"""

import mcp.types as types
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def probe_tools(endpoint: str) -> list[dict]:
    """서버에 접속해 도구를 수집한다. 실패 시 예외 → 호출측에서 OFFLINE 처리."""
    async with streamablehttp_client(endpoint) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            return [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema or {"type": "object", "properties": {}},
                    "output_schema": getattr(t, "outputSchema", None) or {},
                }
                for t in tools
            ]


async def call_upstream(endpoint: str, tool: str, arguments: dict) -> tuple[list[types.ContentBlock], bool]:
    """업스트림 도구를 호출하고 (content, is_error) 를 돌려준다(프록시 중계).
       is_error 는 도구 레벨 오류(없는 도구·도구 내부 예외 등) 표시 — 통계에서 실패로 집계."""
    async with streamablehttp_client(endpoint) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments or {})
            return list(result.content), bool(result.isError)
