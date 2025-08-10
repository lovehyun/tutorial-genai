# 주요 목적: MCP 라이브러리의 구조와 사용법을 이해하기 위해 클래스와 함수들의 문서와 소스코드를 출력합니다.

import inspect
from importlib.metadata import version
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.fastmcp import FastMCP

# 설치된 MCP 라이브러리의 버전을 확인
print(f"\n---\nMCP version: {version('mcp')}")


# FastMCP: MCP 서버를 빠르게 구축하기 위한 클래스
# sse_app: Server-Sent Events 애플리케이션 관련 메서드
print("\n---\nFastMCP class documentation:")
print(inspect.getdoc(FastMCP))
print("\n---\nFastMCP.sse_app method documentation:")
print(inspect.getdoc(FastMCP.sse_app))


# ClientSession: MCP 클라이언트 세션을 관리하는 클래스
# initialize: 클라이언트 세션 초기화 메서드
print("\n---\nClientSession class documentation:")
print(inspect.getdoc(ClientSession))
print("\n---\nClientSession.initialize method documentation:")
print(inspect.getdoc(ClientSession.initialize))
# 주요 특징:
# 세션 관리: 클라이언트-서버 간 지속적인 연결 관리
# 요청/응답 연결: 비동기 요청과 응답을 매칭
# 알림 시스템: 실시간 이벤트 처리
# 진행률 추적: 장시간 작업의 진행 상황 모니터링
# 비동기 컨텍스트 매니저: async with 구문으로 자동 리소스 관리


# streamablehttp_client 함수 검사
print("\n---\nstreamablehttp_client function documentation:")
print(inspect.getdoc(streamablehttp_client))
# streamablehttp_client 함수 시그니처
#
# async def streamablehttp_client(
#     url: str,                                    # MCP 서버 엔드포인트
#     headers: dict[str, Any] | None = None,       # HTTP 헤더
#     timeout: timedelta = timedelta(seconds=30),  # 일반 HTTP 타임아웃
#     sse_read_timeout: timedelta = timedelta(seconds=60 * 5),  # SSE 읽기 타임아웃 (5분)
#     terminate_on_close: bool = True,             # 종료 시 세션 정리 여부
# )
#
# 반환값 구조
# tuple[
#     MemoryObjectReceiveStream[SessionMessage | Exception],  # 수신 스트림
#     MemoryObjectSendStream[SessionMessage],                 # 송신 스트림  
#     GetSessionIdCallback,                                   # 세션 ID 조회 함수
# ]
