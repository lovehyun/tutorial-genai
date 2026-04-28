# MCP 프로토콜 심화

## 과정 정보
- **기간**: 3일 (총 24시간)
- **난이도**: 고급
- **대상**: Claude API와 LangChain 통합 경험이 있고 MCP(Model Context Protocol)를 심도 있게 학습하려는 개발자
- **선수 과목**: 중급 4. 멀티 프로바이더 통합

## 학습 목표
1. MCP 프로토콜의 구조(서버/클라이언트/전송 계층)를 이해할 수 있다
2. MCP 서버와 클라이언트를 직접 구현하고 에이전트에 연결할 수 있다
3. LangChain/LangGraph와 MCP를 브릿지로 통합할 수 있다
4. Claude Desktop에 커스텀 MCP 서버를 등록하고 활용할 수 있다

## 커리큘럼

### Day 1: MCP 기초 — 서버와 클라이언트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | MCP 프로토콜 아키텍처, 환경 설정 |
| 09:30-10:00 | MCP 버전 & 문서 | `4.anthropic/3.mcp/1.intro/1.mcp_version.py`, `4.anthropic/3.mcp/1.intro/2.mcp_docs.py` | MCP 버전 확인, 공식 문서 접근 |
| 10:00-10:30 | Hello MCP | `4.anthropic/3.mcp/1.intro/hello_server.py`, `4.anthropic/3.mcp/1.intro/3.hello_client.py` | 최소 MCP 서버/클라이언트 구현 |
| 10:45-11:15 | Simple 서버 | `4.anthropic/3.mcp/1.intro/simple_server.py`, `4.anthropic/3.mcp/1.intro/simple_server2.py` | 도구를 제공하는 MCP 서버 |
| 11:15-12:00 | Simple 클라이언트 | `4.anthropic/3.mcp/1.intro/5.simple_client.py`, `4.anthropic/3.mcp/1.intro/5.simple_client2_tryexcept.py` | MCP 클라이언트 기본 + 예외 처리 |
| 13:00-13:30 | 클라이언트 정보 조회 | `4.anthropic/3.mcp/1.intro/6.simple_client3_getinfo.py`, `4.anthropic/3.mcp/1.intro/6.simple_client3_getinfo2_tryexcept.py` | 서버 정보 조회, 디버깅 |
| 13:30-14:00 | 디버그 프록시 | `4.anthropic/3.mcp/1.intro/debug_proxy.py` | MCP 통신 디버깅 프록시 |
| 14:00-14:30 | asyncio 이벤트 루프 | `4.anthropic/3.mcp/1.intro/0.asyncio_eventloop/1.asyncio_sep_eventloop_test.py`, `4.anthropic/3.mcp/1.intro/0.asyncio_eventloop/2.asyncio_reuse_eventloop_test.py` | MCP의 비동기 기반 이해 |
| 14:45-15:15 | asyncio 심화 | `4.anthropic/3.mcp/1.intro/0.asyncio_eventloop/3.asyncio_eventloop_test.py`, `4.anthropic/3.mcp/1.intro/0.asyncio_eventloop/4.asyncio_eventloop_test2_stats.py` | 이벤트 루프 재사용, 성능 측정 |
| 15:15-17:00 | 실습: 나만의 MCP 서버/클라이언트 | — | 직접 MCP 서버 설계 및 클라이언트 연결 |

### Day 2: MCP 에이전트와 LangChain 브릿지

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | MCP 기초 복습 |
| 09:30-10:00 | 에이전트 도구 서버 | `4.anthropic/3.mcp/2.agents/1.agent_tool/server.py`, `4.anthropic/3.mcp/2.agents/1.agent_tool/server2.py` | 에이전트용 도구를 제공하는 MCP 서버 |
| 10:00-10:30 | 에이전트 클라이언트 (데모) | `4.anthropic/3.mcp/2.agents/1.agent_tool/1.client_demo.py`, `4.anthropic/3.mcp/2.agents/1.agent_tool/2.client_simple_nlp.py` | 에이전트 클라이언트 기본 |
| 10:45-11:15 | GPT 에이전트 클라이언트 | `4.anthropic/3.mcp/2.agents/1.agent_tool/3.client_gpt.py`, `4.anthropic/3.mcp/2.agents/1.agent_tool/3.client_gpt2_tryexcept.py` | GPT 기반 MCP 에이전트 |
| 11:15-12:00 | 멀티 도구 서버 | `4.anthropic/3.mcp/2.agents/2.multi_tools/math_server.py`, `4.anthropic/3.mcp/2.agents/2.multi_tools/utility_server.py` | 수학/유틸리티 다중 MCP 서버 |
| 13:00-13:30 | 멀티 도구 클라이언트 | `4.anthropic/3.mcp/2.agents/2.multi_tools/1.smart_client_manual.py`, `4.anthropic/3.mcp/2.agents/2.multi_tools/2.smart_client_gpt.py` | 다중 서버 연결 스마트 클라이언트 |
| 13:30-14:00 | HTTP 네트워크 도구 | `4.anthropic/3.mcp/2.agents/3.network_tools/server_http.py`, `4.anthropic/3.mcp/2.agents/3.network_tools/1.client_http.py` | HTTP 기반 MCP 통신 |
| 14:00-14:30 | LangChain 에이전트 (Pydantic) | `4.anthropic/3.mcp/3.langchain_agent/server.py`, `4.anthropic/3.mcp/3.langchain_agent/1.1_client1_pydantic.py` | LangChain + MCP Pydantic 통합 |
| 14:45-15:15 | LangChain 멀티 도구 | `4.anthropic/3.mcp/3.langchain_agent/1.4_client1_multi_tools.py`, `4.anthropic/3.mcp/3.langchain_agent/1.5_client1_multi_tools2_exception.py` | LangChain 멀티 도구 에이전트 |
| 15:15-15:45 | LangChain 브릿지 | `4.anthropic/3.mcp/4.langchain_bridge/mcp_bridge.py`, `4.anthropic/3.mcp/4.langchain_bridge/1.langchain_agent_demo.py` | MCP → LangChain 브릿지 모듈 |
| 15:45-16:15 | LangGraph 브릿지 | `4.anthropic/3.mcp/4.langchain_bridge/3.langgraph_agent_demo.py`, `4.anthropic/3.mcp/4.langchain_bridge/4.langgraph_agent2_demo_except.py` | MCP → LangGraph 브릿지 |
| 16:15-17:00 | 도구 안전성 | `4.anthropic/3.mcp/5.langchain_tools_safety/server.py`, `4.anthropic/3.mcp/5.langchain_tools_safety/1.client.py`, `4.anthropic/3.mcp/5.langchain_tools_safety/2.client2_restrict.py` | 도구 접근 제한, 안전한 에이전트 |

### Day 3: MCP 프로젝트와 Claude Desktop

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | MCP 에이전트, 브릿지 복습 |
| 09:30-10:00 | 파일시스템 서버 | `4.anthropic/3.mcp/10.project_local/1.filesystem/server/server.py`, `4.anthropic/3.mcp/10.project_local/1.filesystem/server/server2.py` | 파일 시스템 접근 MCP 서버 |
| 10:00-10:30 | 파일시스템 클라이언트 | `4.anthropic/3.mcp/10.project_local/1.filesystem/client/client.py`, `4.anthropic/3.mcp/10.project_local/1.filesystem/client/client2.py` | 파일 시스템 MCP 클라이언트 |
| 10:45-11:15 | 파일시스템 MCP 클라이언트 | `4.anthropic/3.mcp/10.project_local/2.filesystem_client/1.fs_mcp_client.py`, `4.anthropic/3.mcp/10.project_local/2.filesystem_client/2.fs_mcp_client2_config.py` | 설정 기반 MCP 클라이언트 |
| 11:15-12:00 | GPT 연동 파일시스템 | `4.anthropic/3.mcp/10.project_local/2.filesystem_client/3.fs_mcp_client3_gpt.py` | GPT + MCP 파일시스템 에이전트 |
| 13:00-13:30 | 리모트 MCP 서버 | `4.anthropic/3.mcp/11.project_remote/1.intro/server/server.py` | 원격 MCP 서버 구성 |
| 13:30-14:00 | 리모트 MCP 클라이언트 | `4.anthropic/3.mcp/11.project_remote/1.intro/client/client.py` | 원격 MCP 클라이언트 연결 |
| 14:00-14:30 | Claude Desktop Hello | `4.anthropic/3.mcp/20.claude_desktop/1.mcp_hello/hello_server.py` | Claude Desktop에 MCP 서버 등록 |
| 14:45-15:15 | Claude Desktop 네트워크 | `4.anthropic/3.mcp/20.claude_desktop/2.simple_net_local/simple_net_check.py`, `4.anthropic/3.mcp/20.claude_desktop/3.simple_net_remote/simple_net_server.py` | 로컬/리모트 네트워크 MCP |
| 15:15-15:45 | 파일 컨버터 서버 | `4.anthropic/3.mcp/20.claude_desktop/4.file_converter/file_converter_server.py`, `4.anthropic/3.mcp/20.claude_desktop/4.file_converter/file_converter2_server_errhandler.py` | 파일 변환 MCP 서버 |
| 15:45-16:15 | 파일 컨버터 테스트 | `4.anthropic/3.mcp/20.claude_desktop/4.file_converter/test_fileconverter_client.py` | MCP 서버 테스트 작성 |
| 16:15-17:00 | 종합 프로젝트 & 발표 | — | 나만의 MCP 서버 구축 및 Claude Desktop 연동, 결과 공유 |

## 환경 설정

```bash
pip install anthropic mcp langchain langchain-anthropic langgraph
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/12_mcp_model_context_protocol.md` | MCP 프로토콜 (서버/클라이언트/전송 계층) |

## 참고 자료
- `4.anthropic/3.mcp/1.intro/` — MCP 기초
- `4.anthropic/3.mcp/2.agents/` — MCP 에이전트
- `4.anthropic/3.mcp/3.langchain_agent/` — LangChain + MCP
- `4.anthropic/3.mcp/4.langchain_bridge/` — LangChain/LangGraph 브릿지
- `4.anthropic/3.mcp/5.langchain_tools_safety/` — 도구 안전성
- `4.anthropic/3.mcp/10.project_local/` — 로컬 MCP 프로젝트
- `4.anthropic/3.mcp/11.project_remote/` — 리모트 MCP 프로젝트
- `4.anthropic/3.mcp/20.claude_desktop/` — Claude Desktop 연동
