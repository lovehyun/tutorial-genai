# 나만의 챗봇 만들기

## 과정 정보
- **기간**: 2일 (총 16시간)
- **난이도**: 입문
- **대상**: API 호출 기초를 익힌 후 실제 동작하는 챗봇을 만들고 싶은 학습자
- **선수 과목**: 입문 1. 생성형 AI API 첫걸음

## 학습 목표
1. Gradio/Flask 기반 챗봇 UI를 구현할 수 있다
2. 대화 히스토리 관리 전략(메모리, SQLite, 세션)을 이해하고 적용할 수 있다
3. 세션 관리와 요약 기능이 포함된 완성도 높은 챗봇을 구축할 수 있다
4. 두 봇이 대화하는 토론봇 시스템을 이해할 수 있다

## 커리큘럼

### Day 1: 챗봇 UI와 히스토리 관리

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 과정 소개, 챗봇 아키텍처 개요 |
| 09:30-10:30 | 챗봇 UI (REST API) | `1.openai/2.chatbot_ui/app_restapi.py` | REST API 기반 기본 챗봇 UI 구현 |
| 10:45-11:30 | 챗봇 UI (SDK) | `1.openai/2.chatbot_ui/app2_openailib.py` | OpenAI SDK로 전환, 코드 간소화 |
| 11:30-12:00 | 히스토리 기초 | `1.openai/3.chatbot2_history/app_restapi.py` | 대화 히스토리의 필요성과 기본 구현 |
| 13:00-13:45 | SDK 히스토리 관리 | `1.openai/3.chatbot2_history/app2_openailib.py`, `1.openai/3.chatbot2_history/app3_history.py` | SDK 기반 히스토리 관리 |
| 13:45-14:30 | 히스토리 제한 | `1.openai/3.chatbot2_history/app4_historylimit.py` | 토큰 비용 제어를 위한 히스토리 제한 전략 |
| 14:45-15:30 | SQLite 영구 저장 | `1.openai/4.chatbot3_historysqlite/app4_historysqlite3.py` | SQLite DB를 활용한 대화 이력 영구 보관 |
| 15:30-16:15 | 프로젝트: 챗봇 GUI | `10.project/1.chatbot_gui/1.openai_sdk/app_restapi.py`, `10.project/1.chatbot_gui/1.openai_sdk/app2_openailib.py` | 프로젝트 수준 챗봇 GUI 분석 |
| 16:15-17:00 | 스트리밍 챗봇 | `10.project/1.chatbot_gui/1.openai_sdk/app3_openailib_stream.py` | 스트리밍 응답이 적용된 챗봇 구현 |

### Day 2: 세션 관리와 토론봇

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:45 | Day 1 복습 | — | 전일 내용 요약, Q&A |
| 09:45-10:30 | 세션 관리 | `1.openai/5.chatbot4_session/app5_session.py` | 사용자별 독립 세션 구현 |
| 10:45-11:30 | 세션 삭제 | `1.openai/5.chatbot4_session/app6_session_delete.py` | 세션 초기화 및 삭제 기능 |
| 11:30-12:00 | 세션 요약 | `1.openai/5.chatbot4_session/app7_session_summary.py` | 긴 대화를 자동 요약하는 메커니즘 |
| 13:00-13:45 | 히스토리 챗봇 완성 | `10.project/1.chatbot_gui/1.openai_sdk/app4_openailib_history.py` | 히스토리가 완비된 최종 챗봇 |
| 13:45-14:30 | 토론봇 기초 | `1.openai/6.twobots/1.debate/bot1.py`, `1.openai/6.twobots/1.debate/bot2.py` | 두 LLM이 토론하는 기본 구조 |
| 14:45-15:30 | 토론봇 고급 | `1.openai/6.twobots/2.debate_advanced/bot1.py`, `1.openai/6.twobots/2.debate_advanced/bot2.py` | 심화 토론봇: 역할 분리, 판정 로직 |
| 15:30-16:15 | LangChain 챗봇 미리보기 | `10.project/1.chatbot_gui/2.langchain/app2_langchain.py` | LangChain 기반 챗봇과의 차이점 비교 |
| 16:15-17:00 | 종합 실습 & 발표 | — | 나만의 챗봇 커스터마이징, 결과 공유 |

## 환경 설정

```bash
pip install openai gradio flask
```

## 참고 자료
- `1.openai/2.chatbot_ui/` — 기본 챗봇 UI
- `1.openai/3.chatbot2_history/` — 히스토리 관리
- `1.openai/4.chatbot3_historysqlite/` — SQLite 저장
- `1.openai/5.chatbot4_session/` — 세션 관리
- `1.openai/6.twobots/` — 토론봇
- `10.project/1.chatbot_gui/` — 완성형 챗봇 프로젝트
