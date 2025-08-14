# LLM 8일차: MCP 개요

## MCP란?
- **Model Context Protocol**의 약자
- LLM ↔ 외부 애플리케이션/서비스 간 **표준화된 양방향 통신 프로토콜**
- LLM이 단순 텍스트 처리에서 벗어나 **OS, 웹, 데이터베이스, API** 등 다양한 리소스에 접근 가능하게 함

---

## 특징
- JSON-RPC 기반의 구조화된 메시지
- **명령(Command)**과 **이벤트(Event)**의 양방향 흐름
- 플러그인처럼 확장 가능
- ChatGPT, Claude 등과 **데스크톱/서버 앱** 간 직접 연동 가능

---

## 주요 구성 요소
1) **MCP Client** — LLM 환경에서 명령을 보내고 응답을 받음
2) **MCP Server** — 특정 리소스에 대한 실제 처리 담당
3) **Schema** — 교환되는 데이터 형식 정의
4) **Transport** — WebSocket, STDIO 등

---

## 예시 흐름
사용자: "폴더 안의 모든 PDF 목록 보여줘"  
↓  
LLM → MCP Client → MCP Server(OS Filesystem Handler) → 파일 목록 반환  
↓  
LLM → 결과 포맷팅 후 사용자에게 응답

---

## 개발 준비
```bash
pip install mcp
```

- Python, Node.js 모두 SDK 제공
- 보안/권한 관리 필수
