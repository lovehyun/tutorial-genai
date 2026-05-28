# 프로젝트 예제

OpenAI API와 LangChain을 활용한 실전 프로젝트 모음입니다.

## 프로젝트 목록

| 디렉토리 | 프로젝트 | 주요 기술 |
|----------|---------|----------|
| `1.chatbot_gui/` | GUI 챗봇 | OpenAI SDK, LangChain, 스트리밍 |
| `1.chatbot_gui_agents/` | 에이전트 챗봇 | LangGraph, 도구 사용 |
| `2.english_learning_flask/` | 영어 학습 | Flask, TTS, 애니메이션 |
| `2.english_learning_nodejs/` | 영어 학습 (Node.js) | Express.js, OpenAI |
| `3.chat_multilingual_flask/` | 다국어 채팅 | Flask, 번역 |
| `3.chat_multilingual_nodejs/` | 다국어 채팅 (Node.js) | Express.js |
| `4.shopreview_summary/` | 리뷰 요약 | LangChain, 번역, 체이닝 |
| `5.seculog_summary/` | 보안 로그 분석 | 로그 요약 |
| `6.code_review_app/` | 코드 리뷰 | 코드 분석, GitHub URL |
| `7.job_match_app/` | 채용 매칭 | RAG, 유사도 검색 |
| `8.exam_grading/` | 시험 채점 | 자동 채점 |
| `9.webtoon_app/` | 웹툰 생성 | DALL-E, 이미지 생성 |
| `10.ai_agent/` | AI 에이전트 | LangGraph |
| `11.mathqna_app/` | 수학 질의응답 | 수식 파싱 |
| `12.nas_mcp_agent/` | NAS MCP 에이전트 | MCP, 파일 검색 |
| `13.document_qa/` | 문서 질의응답 | RAG, PDF |
| `14.musicvibe_app/` | 음악 무드 | 분위기 기반 추천 |
| `15.todo_chatbot/` | **Todo + 챗봇** (3단계 빌드업) | Flask, SQLite, `create_react_agent`, `@tool` |
| `16.airline_chatbot/` | **항공 예약 + 챗봇 + 상담사 연결** (3단계 빌드업) | Flask, SQLite, 에이전트, 권한 분리, 폴링 채팅 |

---

## 단계별 빌드업 프로젝트 (신규)

`15` 과 `16` 은 **단계별 빌드업** 패턴으로 구성된 학습 친화 프로젝트입니다.
각 단계가 자체 폴더에 들어있어 **diff** 로 무엇이 추가됐는지 한눈에 보입니다.

### `15.todo_chatbot/` — Todo CRUD 에 챗봇 점진 결합

| 단계 | 포트 | 추가된 기능 |
|------|------|------------|
| `1.basic_crud/` | 5001 | Flask + SQLite + REST API + 기본 UI (챗봇 X) |
| `2.chatbot_readonly/` | 5002 | + 챗봇 (`list_todos` 도구만 — 조회 / 요약) |
| `3.chatbot_full/` | 5003 | + 자연어 CRUD (`add_todo`/`toggle_done`/`delete_todo`) + 화면 자동 갱신 |

**학습 포인트**: REST API 우선 설계 → 같은 API 를 챗봇 도구로 감싸 권한·기능을 점진 확장.

### `16.airline_chatbot/` — 항공 예약 + 챗봇 + 상담사 연결

| 단계 | 포트 | 추가된 기능 |
|------|------|------------|
| `1.system_base/` | 6001 | 사용자뷰 + 관리자뷰 + DB (항공편/예약/이력) (챗봇 X) |
| `2.chatbot_each_view/` | 6002 | 각 뷰에 **다른 도구 세트**의 에이전트 (권한 분리) |
| `3.consultant_relay/` | 6003 | + **상담사 연결 실시간 채팅** — 챗봇이 `request_consultation` → 관리자 수락 → 2초 폴링으로 양쪽 메시지 송수신 |

**학습 포인트**:
- 같은 LLM 도 도구 세트 분리로 권한 강제 (사용자 챗봇 ≠ 관리자 챗봇)
- 챗봇 한계 인지 → 사람 상담사 에스컬레이션 패턴
- WebSocket 없이 폴링만으로 실시간 채팅 구현

각 프로젝트 폴더에 자체 `README.md` 가 있으니 자세한 내용은 거기에서.
