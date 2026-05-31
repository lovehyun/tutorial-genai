# 프로젝트 예제

OpenAI API · LangChain · LangGraph 를 활용한 실전 프로젝트 모음.

> **난이도 표기**: ★ 입문 · ★★ 중급 · ★★★ 고급
> 폴더 번호 순이 아니라 **카테고리별** 로 묶었습니다.

## 🧭 한눈에

| 그룹 | 핵심 기술 | 추천 학습자 |
|---|---|---|
| **A. 챗봇 / 대화** | 챗봇 UI 기본기 | 시작하는 사람 |
| **B. 언어 / 학습 / 평가** | 텍스트 응용 | 교육·평가 도메인 |
| **C. 텍스트 분석 / 요약 / 리뷰** | 단방향 처리 | 비즈니스·로그·코드 분석 |
| **D. RAG / 문서 검색** | 외부 지식 결합 | 벡터 / 검색 기반 |
| **E. 에이전트 / 도구 사용** | LLM 이 도구 호출 | LangGraph / MCP |
| **F. 멀티모달 / 콘텐츠 생성** | 이미지·음악 | DALL-E / 멀티모달 |
| **G. 종합 빌드업 시리즈** | 단계별 풀스택 | 실전 / 강의 자료 |

추천 학습 순서: **A → B/C → D → E → F → G**

---

## 📂 전체 디렉토리 목록 (폴더 번호 순)

| 디렉토리 | 프로젝트 | 그룹 | 난이도 | 주요 기술 |
|---|---|---|---|---|
| `1.chatbot_gui/` | GUI 챗봇 | A | ★ | OpenAI SDK, LangChain, 스트리밍 |
| `1.chatbot_gui_agents/` | 에이전트 챗봇 | A | ★★ | LangGraph, 도구 사용 |
| `2.english_learning_flask/` | 영어 학습 | B | ★ | Flask, TTS, 애니메이션 |
| `2.english_learning_nodejs/` | 영어 학습 (Node.js) | B | ★ | Express.js, OpenAI |
| `3.chat_multilingual_flask/` | 다국어 채팅 | B | ★ | Flask, 번역 |
| `3.chat_multilingual_nodejs/` | 다국어 채팅 (Node.js) | B | ★ | Express.js |
| `4.shopreview_summary/` | 리뷰 요약 | C | ★ | LangChain, 번역, 체이닝 |
| `5.seculog_summary/` | 보안 로그 분석 | C | ★★ | 로그 요약 |
| `6.code_review_app/` | 코드 리뷰 | C | ★★ | 코드 분석, GitHub URL |
| `7.job_match_app/` | 채용 매칭 | D | ★★ | RAG, 유사도 검색 |
| `8.exam_grading/` | 시험 채점 | B | ★★ | 자동 채점 |
| `9.webtoon_app/` | 웹툰 생성 | F | ★★ | DALL-E, 이미지 생성 |
| `10.ai_agent/` | AI 에이전트 | E | ★★ | LangGraph |
| `11.mathqna_app/` | 수학 질의응답 | B | ★★ | 수식 파싱 |
| `12.nas_mcp_agent/` | NAS MCP 에이전트 | E | ★★★ | MCP, 파일 검색 |
| `13.document_qa/` | 문서 질의응답 | D | ★★ | RAG, PDF |
| `14.musicvibe_app/` | 음악 무드 | F | ★★ | 분위기 기반 추천 |
| `15.todo_chatbot/` | **Todo + 챗봇** (3단계 빌드업) | G | ★★ | Flask, SQLite, `@tool`, `create_react_agent` |
| `16.airline_chatbot/` | **항공 예약 + 챗봇 + 상담사 연결** (3단계 빌드업) | G | ★★★ | Flask, SQLite, 권한 분리, 폴링 채팅 |

---

## A. 챗봇 / 대화 시스템

가장 기본. 챗봇 UI · 스트리밍 · 히스토리.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `1.chatbot_gui/` | ★ | 챗봇 GUI (OpenAI SDK / LangChain 양쪽 버전) | 스트리밍, 히스토리 |
| `1.chatbot_gui_agents/` | ★★ | 에이전트형 챗봇 (계산·메모리·검색 도구) | LangGraph, multi-agent |

## B. 언어 / 학습 / 평가

영어·다국어·수학·시험 — 텍스트 입출력 기반 응용.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `2.english_learning_flask/` | ★ | 영어 학습 (Flask + TTS + 캐릭터 애니메이션) | Flask, TTS |
| `2.english_learning_nodejs/` | ★ | 위 Node.js 포팅 | Express.js |
| `3.chat_multilingual_flask/` | ★ | 다국어 실시간 채팅 (번역 체인) | 번역 chain |
| `3.chat_multilingual_nodejs/` | ★ | 위 Node.js 포팅 | Express.js |
| `8.exam_grading/` | ★★ | 자동 시험 채점 (서술형 평가) | 평가 프롬프트, 점수화 |
| `11.mathqna_app/` | ★★ | 수학 문제 풀이 / 해설 | 수식 파싱, 단계별 풀이 |

## C. 텍스트 분석 / 요약 / 리뷰

긴 입력 → 짧은 인사이트.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `4.shopreview_summary/` | ★ | 상품 리뷰 다국어 요약 | 번역 + 요약 체인 |
| `5.seculog_summary/` | ★★ | 보안 로그 자동 분석 | 로그 파싱 + 요약 |
| `6.code_review_app/` | ★★ | GitHub URL 입력 → 코드 리뷰 | 코드 분석, GitHub API |

## D. RAG / 문서 검색

외부 데이터를 검색해서 LLM 답변에 반영.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `7.job_match_app/` | ★★ | 이력서 ↔ 채용 공고 매칭 | 벡터 유사도, embedding |
| `13.document_qa/` | ★★ | PDF 업로드 후 Q&A | RAG, PyPDFLoader, Chroma |

## E. 에이전트 / 도구 사용

LLM 이 도구를 능동적으로 호출.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `10.ai_agent/` | ★★ | LangGraph 에이전트 점진 발전판 (8단계 버전) | LangGraph, ReAct |
| `12.nas_mcp_agent/` | ★★★ | NAS 파일 검색 / 인덱싱 에이전트 | **MCP**, sqlite 인덱서 |

## F. 멀티모달 / 콘텐츠 생성

텍스트 외 이미지·음악 등 출력.

| 폴더 | 난이도 | 한 줄 설명 | 주요 기술 |
|---|---|---|---|
| `9.webtoon_app/` | ★★ | 줄거리 → 웹툰 자동 생성 | DALL-E 이미지 생성 |
| `14.musicvibe_app/` | ★★ | 음악 분위기 분석/추천 | 멀티모달 / 무드 |

## G. 종합 빌드업 시리즈 ⭐ (단계별 학습)

기본 → 챗봇 추가 → 풀 제어 의 **3단계 폴더 구조** 로, diff 만 봐도 무엇이 추가됐는지 한눈에. 강의 / 실습 자료로 최적.

### `15.todo_chatbot/` — Todo CRUD 에 챗봇 점진 결합 (★★)

| 단계 | 포트 | 추가된 기능 |
|---|---|---|
| `1.basic_crud/` | 5001 | Flask + SQLite + REST API + 기본 UI (챗봇 X) |
| `2.chatbot_readonly/` | 5002 | + 챗봇 (`list_todos` 도구만 — 조회 / 요약) |
| `3.chatbot_full/` | 5003 | + 자연어 CRUD (`add_todo`/`toggle_done`/`delete_todo`) + 화면 자동 갱신 |

**학습 포인트**: REST API 우선 설계 → 같은 API 를 챗봇 도구로 감싸 권한·기능 점진 확장.

### `16.airline_chatbot/` — 항공 예약 + 챗봇 + 상담사 연결 (★★★)

| 단계 | 포트 | 추가된 기능 |
|---|---|---|
| `1.system_base/` | 6001 | 사용자뷰 + 관리자뷰 + DB (항공편/예약/이력) — 챗봇 X |
| `2.chatbot_each_view/` | 6002 | 각 뷰에 **다른 도구 세트**의 에이전트 (권한 분리) |
| `3.consultant_relay/` | 6003 | + **상담사 연결 실시간 채팅** — `request_consultation` → 관리자 수락 → 2초 폴링 |

**학습 포인트**:
- 같은 LLM 도 도구 세트 분리로 권한 강제 (사용자 챗봇 ≠ 관리자 챗봇)
- 챗봇 한계 인지 → 사람 상담사 에스컬레이션 패턴
- WebSocket 없이 폴링만으로 실시간 채팅 구현

---

## 시작 추천

| 처음이라면 | 챗봇 만들고 싶다 | RAG 가 궁금 | 에이전트 / 도구 | 풀스택 실전 |
|---|---|---|---|---|
| A.1.chatbot_gui | A.1.chatbot_gui | D.13.document_qa | E.10.ai_agent | G.15.todo_chatbot |
| → B/C 적당히 | → A.1.agents | → D.7.job_match | → E.12.nas_mcp | → G.16.airline_chatbot |

각 프로젝트 폴더에 자체 `README.md` 가 있으니 자세한 내용은 거기에서.
