# AI 에이전트 개발

## 과정 정보
- **기간**: 3일 (총 24시간)
- **난이도**: 중급
- **대상**: LangChain 체이닝에 익숙하고 도구 사용 에이전트를 개발하고 싶은 개발자
- **선수 과목**: 입문 3. LangChain 핵심 마스터

## 학습 목표
1. LangChain 에이전트의 구조(도구, 메모리, 라우팅)를 이해할 수 있다
2. 내장 도구(Wikipedia, ArXiv, Google 검색)와 커스텀 도구를 만들고 결합할 수 있다
3. Human-in-the-Loop 에이전트를 설계할 수 있다
4. 다중 도구 복합 에이전트와 스마트 라우터를 구현할 수 있다

## 커리큘럼

### Day 1: 에이전트 기초와 내장 도구

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | 에이전트 아키텍처 개요, ReAct 패턴 |
| 09:30-10:00 | 에이전트 기본 역량 | `2.langchain/8.agents/1.builtin_tools/1.0_list_all_tools.py` | 에이전트가 쓸 수 있는 빌트인 도구 카탈로그 탐색 |
| 10:00-10:30 | 수학 도구 에이전트 | `2.langchain/7.agents/1.1_llmmath.py` <!-- TODO: 경로 확인 필요 --> | LLMMath 도구 기반 에이전트 |
| 10:45-11:15 | Wikipedia 에이전트 | `2.langchain/8.agents/0.legacy(initialize_agent)/1.wikipedia/2.1_wikipedia1.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/1.wikipedia/2.2_wikipedia1_ko.py` | Wikipedia 검색 (영어/한국어) |
| 11:15-12:00 | Wikipedia + Math 복합 | `2.langchain/8.agents/0.legacy(initialize_agent)/1.wikipedia/2.3_wikipedia2_math.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/1.wikipedia/2.5_wikipedia3_structured_output.py` | 다중 도구 결합, Structured Output |
| 13:00-13:45 | ArXiv 논문 검색 | `2.langchain/8.agents/0.legacy(initialize_agent)/2.arxiv/3.1_arxiv_thesis.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/2.arxiv/3.2_arxiv_thesis2_detail.py` | ArXiv API로 논문 검색 |
| 13:45-14:30 | ArXiv 에이전트 & 번역 | `2.langchain/8.agents/0.legacy(initialize_agent)/2.arxiv/3.3_arxiv_thesis2_detail2_agent.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/2.arxiv/3.4_arxiv_thesis3_translate.py` | 에이전트 기반 논문 검색, 자동 번역 |
| 14:45-15:30 | 번역 체이닝 | `2.langchain/8.agents/0.legacy(initialize_agent)/2.arxiv/3.5_arxiv_thesis3_translate2_chaining.py` | 검색 → 번역 체이닝 자동화 |
| 15:30-17:00 | 실습: 나만의 리서치 에이전트 | — | Wikipedia + ArXiv 결합 에이전트 구축 |

### Day 2: 커스텀 도구와 Human-in-the-Loop

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 에이전트 기초 복습 |
| 09:30-10:00 | 커스텀 도구 (기초) | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.1_customtools1_add.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.2_customtools1_addmultiply.py` | @tool 데코레이터로 커스텀 도구 생성 |
| 10:00-10:30 | 커스텀 도구 (완성) | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.3_customtools1_addmultiply2_final.py` | 완성형 커스텀 도구 에이전트 |
| 10:45-11:15 | 정보 조회 도구 | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.4_customtools2_getinfo.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.5_customtools2_getinfo2_structured.py` | 외부 정보 조회 + Structured Output |
| 11:15-12:00 | 웹 검색 도구 (Serper) | `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.6_customtools3_serper.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/3.custom_tools/4.7_customtools3_serper2_detail.py` | Serper API 연동 웹 검색 |
| 13:00-13:45 | Human Agent 기초 | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.1_humanagent.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.2_humanagent2_detail.py` | 사람 개입이 필요한 에이전트 |
| 13:45-14:30 | Human Agent 커스텀 | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.3_humanagent2_custom.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.4_humanagent2_custom2_gui.py` | 커스텀 Human Agent, GUI 통합 |
| 14:45-15:30 | Human + 웹검색 미니/풀 | `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.5_humanagent4_websearchmini.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/4.human_in_loop/5.6_humanagent4_websearchfull.py` | Human + 웹검색 결합 에이전트 |
| 15:30-17:00 | 실습: HITL 에이전트 구축 | — | Human-in-the-Loop 에이전트 직접 구현 |

### Day 3: 복합 에이전트와 프로젝트

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 | — | 커스텀 도구, HITL 복습 |
| 09:30-10:00 | 의사결정 에이전트 | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/6.1_decide_human_serper.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/6.2_decide2_serper_wiki.py` | 도구 자동 선택 라우팅 |
| 10:00-10:30 | Google 검색 에이전트 | `2.langchain/8.agents/0.legacy(initialize_agent)/6.googlesearch/7.1_googlesearch.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/6.googlesearch/7.2_googlesearch2_detail.py` | Google 검색 API 연동 |
| 10:45-11:15 | 검색 + 번역 통합 | `2.langchain/8.agents/0.legacy(initialize_agent)/6.googlesearch/7.3_googlesearch3_translate.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/6.googlesearch/7.4_googlesearch4_onechain.py` | 검색 → 번역 원체인 구성 |
| 11:15-12:00 | 복합 에이전트 | `2.langchain/8.agents/0.legacy(initialize_agent)/7.complex/8.1_complex.py` | 다중 도구 복합 에이전트 설계 |
| 13:00-13:30 | 스마트 에이전트 | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.1_smartagent.py` | 자율 판단 스마트 에이전트 |
| 13:30-14:00 | 스마트 라우터 | `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.2_smartagent_router.py`, `2.langchain/8.agents/0.legacy(initialize_agent)/5.routing/9.3_smartagent_router2_moretools.py` | 도구별 라우팅 시스템 |
| 14:00-14:30 | 웹 스캔 에이전트 | `2.langchain/8.agents/10.mini_apps/1.webscan_app/app.py` | 웹 스캐닝 에이전트 앱 |
| 14:45-15:30 | AI 에이전트 프로젝트 | `10.project/10.ai_agent/app.py`, `10.project/10.ai_agent/app2_history.py`, `10.project/10.ai_agent/app3_metadata.py` | 프로젝트 수준 에이전트 분석 |
| 15:30-16:15 | 멀티 에이전트 | `10.project/10.ai_agent/app6_multi_agent.py`, `10.project/10.ai_agent/app8_multi_agent3_final.py` | 멀티 에이전트 시스템 분석 |
| 16:15-17:00 | 종합 프로젝트 & 발표 | — | 나만의 복합 에이전트 구축, 결과 공유 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-community wikipedia arxiv google-search-results flask
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/09_ai_agent_overview.md` | AI 에이전트 개요 (ReAct, 도구 사용) |

## 참고 자료
- `2.langchain/8.agents/` — LangChain 에이전트 전체 (옛 `initialize_agent` 예제는 `0.legacy(initialize_agent)/`, 현행 예제는 `1.builtin_tools/`~`9.agentic_patterns/`)
- `10.project/10.ai_agent/` — AI 에이전트 프로젝트
