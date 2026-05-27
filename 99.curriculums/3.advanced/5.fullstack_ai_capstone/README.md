# 풀스택 AI 캡스톤

## 과정 정보
- **기간**: 5일 (총 40시간)
- **난이도**: 고급
- **대상**: 중급 과정을 전체 수료하고 실전 프로젝트 경험을 쌓고 싶은 개발자
- **선수 과목**: 중급 전체 수료 권장 (최소: 중급 1. RAG 마스터클래스 + 중급 2. AI 에이전트 개발)

## 학습 목표
1. 매일 2~3개의 프로덕션 수준 프로젝트를 분석하고 직접 구축할 수 있다
2. Flask/Gradio 기반 풀스택 AI 앱의 설계-구현-배포 전 과정을 경험할 수 있다
3. 자유 주제 캡스톤 프로젝트를 기획-설계-구현-발표할 수 있다

## 커리큘럼

### Day 1: 챗봇 & 영어학습 프로젝트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 5일 과정 로드맵, 프로젝트 개발 방법론 |
| 09:30-10:00 | 챗봇 (REST → SDK) | `10.project/1.chatbot_gui/1.openai_sdk/app_restapi.py`, `10.project/1.chatbot_gui/1.openai_sdk/app2_openailib.py` | 챗봇 기본 구조 분석 |
| 10:00-10:30 | 챗봇 (스트리밍/히스토리) | `10.project/1.chatbot_gui/1.openai_sdk/app3_openailib_stream.py`, `10.project/1.chatbot_gui/1.openai_sdk/app4_openailib_history.py` | 스트리밍, 히스토리 구현 |
| 10:45-11:15 | 챗봇 (LangChain) | `10.project/1.chatbot_gui/2.langchain/app2_langchain.py`, `10.project/1.chatbot_gui/2.langchain/app3_langchain_stream.py` | LangChain 전환 |
| 11:15-12:00 | 실습: 나만의 챗봇 확장 | — | 기능 추가 (다국어, 테마, 파일 업로드 등) |
| 13:00-13:30 | 영어학습 (기초 웹) | `10.project/2.english_learning_flask/1.basic_web/app.py` | Flask 웹 앱 기초 |
| 13:30-14:00 | 영어학습 (OpenAI) | `10.project/2.english_learning_flask/2.openai/app.py`, `10.project/2.english_learning_flask/2.openai/app2_langchain.py` | AI 기반 영어학습 앱 |
| 14:00-14:30 | 영어학습 (로깅/백엔드) | `10.project/2.english_learning_flask/2.openai/app3_logging.py`, `10.project/2.english_learning_nodejs/backend/app.py` | 로깅, 별도 백엔드 |
| 14:45-15:30 | 다국어 채팅 앱 | `10.project/3.chat_multilingual_flask/app.py` | 다국어 지원 채팅 앱 분석 및 확장 |
| 15:30-17:00 | 실습: 영어학습 앱 확장 | — | 문법 교정, 발음 평가, 작문 피드백 등 기능 추가 |

### Day 2: 비즈니스 분석 프로젝트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 챗봇/영어학습 프로젝트 복습 |
| 09:30-10:00 | 리뷰 요약 (기초) | `10.project/4.shopreview_summary/app.py`, `10.project/4.shopreview_summary/app2_trans.py` | 리뷰 요약 기본 |
| 10:00-10:30 | 리뷰 요약 (LangChain) | `10.project/4.shopreview_summary/app3_trans_langchain.py`, `10.project/4.shopreview_summary/app4_trans_langchain2_runnables.py` | LCEL 기반 리팩터링 |
| 10:45-11:15 | 보안로그 분석 | `10.project/5.seculog_summary/app.py`, `10.project/5.seculog_summary/app2_logdiff.py` | 보안 로그 요약/비교 |
| 11:15-12:00 | 실습: 비즈니스 분석 앱 | — | 리뷰/로그 분석 앱 커스터마이징 |
| 13:00-13:30 | 코드리뷰 (OpenAI) | `10.project/6.code_review_app/1.openai/app1_textarea.py`, `10.project/6.code_review_app/1.openai/app2_githuburl.py` | 코드리뷰 앱 기본 |
| 13:30-14:00 | 코드리뷰 (통합) | `10.project/6.code_review_app/3.common/app3_improvedisplay_common.py`, `10.project/6.code_review_app/3.common/app4_fileseparate.py` | 멀티 프로바이더 통합 코드리뷰 |
| 14:00-14:30 | 취업 매칭 앱 | `10.project/7.job_match_app/1.basic/app.py`, `10.project/7.job_match_app/3.design/app.py` | 이력서-직무 매칭 |
| 14:45-15:30 | 시험채점 앱 | `10.project/8.exam_grading/1.simple/exam_grading.py`, `10.project/8.exam_grading/3.flask/web/app.py` | LLM 기반 채점 시스템 |
| 15:30-17:00 | 실습: 비즈니스 앱 구축 | — | 자유 주제 비즈니스 분석 앱 구축 |

### Day 3: 크리에이티브 & 고급 프로젝트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | 비즈니스 프로젝트 복습 |
| 09:30-10:00 | 웹툰 생성 (기초) | `10.project/9.webtoon_app/1.basic_flask/app.py`, `10.project/9.webtoon_app/1.basic_flask/app2_langchain.py` | 텍스트 → 웹툰 이미지 |
| 10:00-10:30 | 웹툰 생성 (안전성/동적) | `10.project/9.webtoon_app/1.basic_flask/app3_imagesafety.py`, `10.project/9.webtoon_app/2.dynamic_update/app.py` | 이미지 안전성, 동적 업데이트 |
| 10:45-11:15 | 에이전트 챗봇 | `10.project/1.chatbot_gui_agents/app.py`, `10.project/1.chatbot_gui_agents/agents/agent_manager.py` | 에이전트 기반 지능형 챗봇 |
| 11:15-12:00 | 실습: 크리에이티브 앱 확장 | — | 웹툰/에이전트 챗봇 커스터마이징 |
| 13:00-13:30 | 수학 QnA 앱 | `10.project/11.mathqna_app/app.py`, `10.project/11.mathqna_app/services/ai_service.py` | 수학 문제 출제/풀이 |
| 13:30-14:00 | 문서 QA 앱 | `10.project/13.document_qa/app.py` | RAG 기반 문서 QA |
| 14:00-14:30 | NAS MCP 에이전트 | `10.project/12.nas_mcp_agent/1.mcp_filescan_nodb.py`, `10.project/12.nas_mcp_agent/3.mcp_filescan_indexer_db.py` | NAS 파일 관리 에이전트 |
| 14:45-15:30 | 멀티에이전트 시스템 | `10.project/10.ai_agent/app6_multi_agent.py`, `10.project/10.ai_agent/app8_multi_agent3_final.py` | 멀티에이전트 프로젝트 |
| 15:30-17:00 | 캡스톤 주제 선정 & 설계 | — | 자유 캡스톤 주제 선정, 아키텍처 설계 |

### Day 4: 캡스톤 프로젝트 개발

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 캡스톤 개발 가이드 | — | 개발 전략, 코드 리뷰 체크리스트 |
| 09:30-12:00 | 캡스톤 개발 (오전) | — | 자유 주제 프로젝트 개발, 멘토 순회 지도 |
| 13:00-14:30 | 캡스톤 개발 (오후 1) | — | 프로젝트 개발 계속 |
| 14:45-16:00 | 캡스톤 개발 (오후 2) | — | 기능 완성, 테스트, 문서화 |
| 16:00-17:00 | 중간 점검 & 피드백 | — | 진행 상황 공유, 상호 피드백 |

### Day 5: 캡스톤 완성 & 발표

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 캡스톤 마무리 안내 | — | 발표 준비 가이드, 최종 점검 사항 |
| 09:30-12:00 | 캡스톤 최종 개발 | — | 버그 수정, UI 마무리, 발표 자료 준비 |
| 13:00-15:00 | 캡스톤 발표 | — | 개인/팀별 프로젝트 발표 (15분/팀) |
| 15:00-16:00 | 상호 평가 & 피드백 | — | 동료 평가, 강사 피드백 |
| 16:00-17:00 | 전체 과정 회고 & 수료 | — | 5주간 커리큘럼 총정리, 향후 학습 로드맵, 수료식 |

## 환경 설정

```bash
pip install openai anthropic langchain langchain-openai langchain-anthropic langgraph chromadb flask gradio pypdf mcp
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/06_genai_applied/` | 전체 응용 프로젝트 교안 (문서QA, 코드리뷰, 채점, 검색엔진, 콘텐츠생성, 에이전트) |

## 참고 자료
- `10.project/` — 전체 프로젝트 디렉토리
  - `1.chatbot_gui/` — 챗봇 GUI
  - `1.chatbot_gui_agents/` — 에이전트 챗봇
  - `2.english_learning_flask/` — 영어학습
  - `3.chat_multilingual_flask/` — 다국어 채팅
  - `4.shopreview_summary/` — 리뷰 요약
  - `5.seculog_summary/` — 보안로그 분석
  - `6.code_review_app/` — 코드리뷰
  - `7.job_match_app/` — 취업 매칭
  - `8.exam_grading/` — 시험채점
  - `9.webtoon_app/` — 웹툰 생성
  - `10.ai_agent/` — AI 에이전트
  - `11.mathqna_app/` — 수학 QnA
  - `12.nas_mcp_agent/` — NAS MCP 에이전트
  - `13.document_qa/` — 문서 QA
