# 주요 목적: MCP 라이브러리의 구조와 사용법을 이해하기 위해 클래스와 함수들의 문서와 소스코드를 출력합니다.

import inspect
from importlib.metadata import version
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.fastmcp import FastMCP

# 설치된 MCP 라이브러리의 버전을 확인
print(f"MCP version: {version('mcp')}")


# FastMCP: MCP 서버를 빠르게 구축하기 위한 클래스
# sse_app: Server-Sent Events 애플리케이션 관련 메서드
print("\nFastMCP class documentation:")
print(inspect.getdoc(FastMCP))
print("\nFastMCP.sse_app method documentation:")
print(inspect.getdoc(FastMCP.sse_app))


# ClientSession: MCP 클라이언트 세션을 관리하는 클래스
# initialize: 클라이언트 세션 초기화 메서드
print("\nClientSession class documentation:")
print(inspect.getdoc(ClientSession))
print("\nClientSession.initialize method documentation:")
print(inspect.getdoc(ClientSession.initialize))
# 주요 특징:
# 세션 관리: 클라이언트-서버 간 지속적인 연결 관리
# 요청/응답 연결: 비동기 요청과 응답을 매칭
# 알림 시스템: 실시간 이벤트 처리
# 진행률 추적: 장시간 작업의 진행 상황 모니터링
# 비동기 컨텍스트 매니저: async with 구문으로 자동 리소스 관리


# streamablehttp_client 함수 검사
print("\nstreamablehttp_client function documentation:")
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

print("\nImplementation of streamablehttp_client:")
print(inspect.getsource(streamablehttp_client))

# 1. 스트림 생성
# pythonread_stream_writer, read_stream = anyio.create_memory_object_stream[SessionMessage | Exception](0)
# write_stream, write_stream_reader = anyio.create_memory_object_stream[SessionMessage](0)
#
# 양방향 통신: 읽기/쓰기 스트림 분리
# 메모리 기반: 고성능 인메모리 스트림
# 타입 안전성: 제네릭을 통한 메시지 타입 보장

# 2. 동시성 관리
# pythonasync with anyio.create_task_group() as tg:
#
# AnyIO 태스크 그룹: 여러 비동기 작업을 동시에 관리
# 구조화된 동시성: 모든 태스크가 함께 시작되고 종료

# 3. HTTP 클라이언트 설정
# pythonasync with create_mcp_http_client(
#     headers=transport.request_headers,
#     timeout=httpx.Timeout(transport.timeout.seconds, read=transport.sse_read_timeout.seconds),
# ) as client:
#
# HTTPX 기반: 현대적인 비동기 HTTP 클라이언트
# 차별화된 타임아웃: 일반 요청과 SSE 읽기에 서로 다른 타임아웃 적용

# 4. 동시 작업 실행
# pythontg.start_soon(transport.handle_get_stream, client, read_stream_writer)  # SSE 수신
# tg.start_soon(transport.post_writer, client, write_stream_reader, ...)  # HTTP POST 송신
# 실제 사용 시나리오
# 기본 사용 패턴
# pythonasync with streamablehttp_client("http://localhost:8000/mcp") as (read_stream, write_stream, get_session_id):
#     async with ClientSession(read_stream, write_stream) as session:
#         # MCP 통신 수행
#         await session.initialize()
#         # 실제 작업...
# 타임아웃 설정의 의미
#
# 일반 타임아웃 (30초): POST 요청, 초기 연결 등
# SSE 타임아웃 (5분): 실시간 이벤트 수신 대기 시간
# 장시간 작업: AI 모델 추론 등 시간이 오래 걸리는 작업 고려
#
# 아키텍처의 장점
#
# 확장성: 스트림 기반으로 대용량 데이터 처리 가능
# 안정성: 구조화된 동시성으로 리소스 누수 방지
# 유연성: 다양한 타임아웃 설정으로 용도별 최적화
# 실시간성: SSE를 통한 즉시 응답 처리
#
# 이 구조는 AI 에이전트가 외부 도구나 서비스와 안정적이고 효율적으로 통신할 수 있도록 설계된 현대적인 비동기 통신 프레임워크입니다.
