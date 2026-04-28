# 프로덕션 LLM 앱

## 과정 정보
- **기간**: 3일 (총 24시간)
- **난이도**: 고급
- **대상**: RAG와 에이전트를 학습한 후 실전 Flask 앱을 구축하고 싶은 개발자
- **선수 과목**: 중급 1. RAG 마스터클래스

## 학습 목표
1. Flask 기반 LLM 웹 앱의 설계 패턴(라우팅, 서비스 분리, 에러 처리)을 이해할 수 있다
2. 영어학습, 리뷰 요약, 보안로그 분석, 코드리뷰, 시험채점 등 6종의 실전 앱을 분석하고 확장할 수 있다
3. 에이전트 기반 챗봇과 문서 QA 앱을 포함한 고급 프로젝트를 구현할 수 있다

## 커리큘럼

### Day 1: 챗봇 앱과 영어학습 앱

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 프로덕션 앱 아키텍처, 프로젝트 개요 |
| 09:30-10:00 | 챗봇 GUI (OpenAI) | `10.project/1.chatbot_gui/1.openai_sdk/app_restapi.py`, `10.project/1.chatbot_gui/1.openai_sdk/app2_openailib.py` | REST API → SDK 챗봇 |
| 10:00-10:30 | 챗봇 GUI (스트리밍/히스토리) | `10.project/1.chatbot_gui/1.openai_sdk/app3_openailib_stream.py`, `10.project/1.chatbot_gui/1.openai_sdk/app4_openailib_history.py` | 스트리밍, 히스토리 적용 |
| 10:45-11:15 | 챗봇 GUI (LangChain) | `10.project/1.chatbot_gui/2.langchain/app2_langchain.py`, `10.project/1.chatbot_gui/2.langchain/app3_langchain_stream.py` | LangChain 기반 챗봇 |
| 11:15-12:00 | 에이전트 챗봇 | `10.project/1.chatbot_gui_agents/app.py`, `10.project/1.chatbot_gui_agents/agents/agent_manager.py` | 에이전트 관리자 기반 지능형 챗봇 |
| 13:00-13:30 | 에이전트 모듈 분석 | `10.project/1.chatbot_gui_agents/agents/chat_agent.py`, `10.project/1.chatbot_gui_agents/agents/search_agent.py` | 챗/검색/계산 에이전트 모듈 |
| 13:30-14:00 | 영어학습 앱 (기초 웹) | `10.project/2.english_learning_flask/1.basic_web/app.py` | Flask 기본 웹 앱 구조 |
| 14:00-14:30 | 영어학습 앱 (OpenAI) | `10.project/2.english_learning_flask/2.openai/app.py`, `10.project/2.english_learning_flask/2.openai/app2_langchain.py` | OpenAI/LangChain 연동 영어학습 |
| 14:45-15:30 | 영어학습 앱 (로깅) | `10.project/2.english_learning_flask/2.openai/app3_logging.py` | 프로덕션 로깅 적용 |
| 15:30-16:15 | 영어학습 (Node.js 백엔드) | `10.project/2.english_learning_nodejs/backend/app.py`, `10.project/2.english_learning_nodejs/backend/app2_langchain.py` | Node.js 프론트엔드 + Python 백엔드 |
| 16:15-17:00 | 다국어 채팅 앱 | `10.project/3.chat_multilingual_flask/app.py` | 다국어 지원 채팅 앱, Day 1 정리 |

### Day 2: 비즈니스 앱 — 리뷰 요약 · 보안로그 · 시험채점

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 챗봇/영어학습 앱 패턴 복습 |
| 09:30-10:00 | 쇼핑 리뷰 요약 (기초) | `10.project/4.shopreview_summary/app.py` | 리뷰 텍스트 요약 기본 |
| 10:00-10:30 | 리뷰 요약 (번역) | `10.project/4.shopreview_summary/app2_trans.py`, `10.project/4.shopreview_summary/app3_trans_langchain.py` | 번역 + 요약 결합 |
| 10:45-11:15 | 리뷰 요약 (LCEL) | `10.project/4.shopreview_summary/app4_trans_langchain2_runnables.py` | LCEL Runnables 기반 리팩터링 |
| 11:15-12:00 | 보안로그 분석 (기초) | `10.project/5.seculog_summary/app.py`, `10.project/5.seculog_summary/log_generator.py` | 보안 로그 생성기와 분석 앱 |
| 13:00-13:30 | 보안로그 분석 (로그 비교) | `10.project/5.seculog_summary/app2_logdiff.py`, `10.project/5.seculog_summary/utils/log_utils.py` | 로그 비교 분석, 유틸리티 모듈 |
| 13:30-14:00 | 시험채점 (단순) | `10.project/8.exam_grading/1.simple/exam_grading.py` | LLM 기반 시험 답안 채점 |
| 14:00-14:30 | 시험채점 (RPC) | `10.project/8.exam_grading/2.rpcstyle/file_server.py`, `10.project/8.exam_grading/2.rpcstyle/grading_client.py` | RPC 스타일 채점 시스템 |
| 14:45-15:15 | 시험채점 (Flask 웹) | `10.project/8.exam_grading/3.flask/web/app.py`, `10.project/8.exam_grading/3.flask/grading_client.py` | Flask 웹 기반 채점 시스템 |
| 15:15-15:45 | 취업 매칭 앱 (기초) | `10.project/7.job_match_app/1.basic/app.py`, `10.project/7.job_match_app/1.basic/routes.py` | 이력서-직무 매칭 기본 |
| 15:45-16:15 | 취업 매칭 앱 (비교/디자인) | `10.project/7.job_match_app/2.compare/app.py`, `10.project/7.job_match_app/3.design/app.py` | 비교 기능, UI 디자인 개선 |
| 16:15-17:00 | Day 2 정리 & Q&A | — | 비즈니스 앱 패턴 정리 |

### Day 3: 고급 프로젝트 — 웹툰 · 수학QnA · 문서QA · NAS

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | 비즈니스 앱 핵심 복습 |
| 09:30-10:00 | 웹툰 생성 앱 (기초) | `10.project/9.webtoon_app/1.basic_flask/app.py`, `10.project/9.webtoon_app/1.basic_flask/app2_langchain.py` | 텍스트 → 웹툰 이미지 생성 |
| 10:00-10:30 | 웹툰 앱 (안전성/상세) | `10.project/9.webtoon_app/1.basic_flask/app3_imagesafety.py`, `10.project/9.webtoon_app/1.basic_flask/app2_detailed.py` | 이미지 안전성 검사, 상세 버전 |
| 10:45-11:15 | 웹툰 동적 업데이트 | `10.project/9.webtoon_app/2.dynamic_update/app.py` | 실시간 동적 웹툰 업데이트 |
| 11:15-12:00 | 수학 QnA 앱 | `10.project/11.mathqna_app/app.py`, `10.project/11.mathqna_app/services/ai_service.py` | 수학 문제 출제/풀이 앱 |
| 13:00-13:30 | 수학 QnA 설정 | `10.project/11.mathqna_app/config/problems.py`, `10.project/11.mathqna_app/config/settings.py` | 문제 풀, 설정 관리 모듈 |
| 13:30-14:00 | 문서 QA 앱 | `10.project/13.document_qa/app.py` | RAG 기반 문서 질의응답 앱 |
| 14:00-14:30 | NAS MCP 에이전트 | `10.project/12.nas_mcp_agent/1.mcp_filescan_nodb.py`, `10.project/12.nas_mcp_agent/2.mcp_filescan_contents_nodb.py` | NAS 파일 스캔 MCP 에이전트 |
| 14:45-15:15 | NAS 인덱서 | `10.project/12.nas_mcp_agent/3.mcp_filescan_indexer_db.py` | DB 기반 NAS 파일 인덱싱 |
| 15:15-17:00 | 종합 프로젝트 & 발표 | — | 자유 주제 앱 확장/신규 구축, 결과 발표 |

## 환경 설정

```bash
pip install openai langchain langchain-openai flask gradio chromadb pypdf
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/06_genai_applied/01_document_qa_chatbot.md` | 문서 QA 챗봇 설계 |
| `0.docs/06_genai_applied/02_code_review_service.md` | 코드 리뷰 서비스 |
| `0.docs/06_genai_applied/03_exam_grading_service.md` | 시험 채점 서비스 |
| `0.docs/06_genai_applied/05_content_generation.md` | 콘텐츠 생성 (웹툰 등) |

## 참고 자료
- `10.project/1.chatbot_gui/` — 챗봇 GUI 프로젝트
- `10.project/1.chatbot_gui_agents/` — 에이전트 챗봇
- `10.project/2.english_learning_flask/` — 영어학습 앱
- `10.project/4.shopreview_summary/` — 리뷰 요약
- `10.project/5.seculog_summary/` — 보안로그 분석
- `10.project/6.code_review_app/` — 코드리뷰 앱
- `10.project/7.job_match_app/` — 취업 매칭
- `10.project/8.exam_grading/` — 시험채점
- `10.project/9.webtoon_app/` — 웹툰 생성
- `10.project/11.mathqna_app/` — 수학 QnA
- `10.project/12.nas_mcp_agent/` — NAS MCP 에이전트
- `10.project/13.document_qa/` — 문서 QA
