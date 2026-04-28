# LangChain 핵심 마스터

## 과정 정보
- **기간**: 2일 (총 16시간)
- **난이도**: 입문
- **대상**: OpenAI API 사용 경험이 있고 LangChain 프레임워크를 체계적으로 학습하려는 개발자
- **선수 과목**: 입문 1. 생성형 AI API 첫걸음

## 학습 목표
1. LangChain의 핵심 구성요소(Model, Prompt, Parser, Chain, Memory)를 이해하고 활용할 수 있다
2. LCEL(LangChain Expression Language) 기반 체이닝 패턴을 구현할 수 있다
3. 다양한 메모리 전략을 비교하고 상황에 맞게 적용할 수 있다

## 커리큘럼

### Day 1: 모델 · 프롬프트 · 파서 · 체이닝

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | 오리엔테이션 | — | LangChain 아키텍처 개요, 환경 설정 |
| 09:30-10:00 | 모델 종류 비교 | `2.langchain/1.llm_models/0.models.py` | LangChain 지원 모델 목록과 차이 |
| 10:00-10:30 | LLM 모델 호출 | `2.langchain/1.llm_models/1.1_openai_completion.py`, `2.langchain/1.llm_models/1.2_openai2_chat.py` | Completion vs Chat 모델 |
| 10:45-11:15 | 프롬프트 템플릿 기초 | `2.langchain/2.prompts/1.1_template.py`, `2.langchain/2.prompts/1.2_template_invoke.py` | PromptTemplate 생성과 invoke |
| 11:15-12:00 | 프롬프트 체이닝 | `2.langchain/2.prompts/2.1_template_chaining.py`, `2.langchain/2.prompts/2.2_template_chaining2_lambda.py` | 프롬프트 간 체이닝, Lambda 활용 |
| 13:00-13:30 | Chat 프롬프트 | `2.langchain/2.prompts/3.1_template_chat.py`, `2.langchain/2.prompts/3.2_template_chat_chaining.py` | ChatPromptTemplate와 역할 분리 |
| 13:30-14:00 | 실전 프롬프트 (요약/번역) | `2.langchain/2.prompts/4.1_summarization_instruct.py`, `2.langchain/2.prompts/4.3_translation_instruct.py` | 요약, 번역 프롬프트 패턴 |
| 14:00-14:30 | 실전 프롬프트 (이메일/SQL) | `2.langchain/2.prompts/4.5_emailgeneration_instruct.py`, `2.langchain/2.prompts/4.7_sqlgeneration_instruct.py` | 이메일 생성, SQL 생성 |
| 14:45-15:15 | Output Parser | `2.langchain/3.structured_output/1.str_output_parser.py`, `2.langchain/3.structured_output/2.pydantic_parser.py` | 문자열, Pydantic 파서 |
| 15:15-15:45 | Structured Output | `2.langchain/3.structured_output/3.with_structured_output.py` | with_structured_output 메서드 |
| 15:45-16:15 | LCEL 체이닝 기초 | `2.langchain/4.chaining/1.1_prompttemplate_instruct.py`, `2.langchain/4.chaining/1.2_prompttemplate_chat.py` | 파이프 연산자(|) 기반 LCEL |
| 16:15-17:00 | RunnableLambda | `2.langchain/4.chaining/2.1_runnablelambda_instruct.py`, `2.langchain/4.chaining/2.4_runnablelambda4_chat_scoring.py` | 커스텀 함수를 체인에 삽입 |

### Day 2: 고급 체이닝 · 메모리 · 종합 실습

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 전일 내용 요약, Q&A |
| 09:30-10:00 | RunnablePassthrough | `2.langchain/4.chaining/3.1_runnablepassthrough_instruct.py`, `2.langchain/4.chaining/3.2_runnablepassthrough2_chat.py` | 입력 데이터 통과 패턴 |
| 10:00-10:30 | 병렬 체이닝 | `2.langchain/4.chaining/4.1_runnableparallel_chat.py`, `2.langchain/4.chaining/5.1_runnablemap_chat.py` | RunnableParallel, RunnableMap |
| 10:45-11:15 | 프로덕션 패턴 | `2.langchain/4.chaining/7.1_production_fallback_retry.py` | Fallback, Retry 전략 |
| 11:15-12:00 | Flask 연동 | `2.langchain/1.llm_models/2.1_openai_flask_api.py`, `2.langchain/1.llm_models/2.2_openai2_flask_fe.py` | LangChain + Flask API 서버 |
| 13:00-13:30 | 메모리 없는 대화 | `2.langchain/5.memory/1.1_nomemory.py`, `2.langchain/5.memory/1.2_nomemory2_chatbot_cli.py` | 메모리 없는 챗봇의 한계 체험 |
| 13:30-14:00 | 메모리 기본 | `2.langchain/5.memory/3.1_memory_new.py`, `2.langchain/5.memory/3.2_memory2_file.py` | 새로운 메모리 API, 파일 저장 |
| 14:00-14:30 | SQLite 메모리 | `2.langchain/5.memory/3.3_memory3_sqlite.py` | SQLite 기반 영구 메모리 |
| 14:45-15:15 | 히스토리 & 세션 | `2.langchain/5.memory/4.1_history.py`, `2.langchain/5.memory/4.2_history2_session.py` | ChatMessageHistory, 세션 관리 |
| 15:15-15:45 | 히스토리 요약 | `2.langchain/5.memory/5.2_history_summary_new.py`, `2.langchain/5.memory/5.3_history_summary2_session.py` | 대화 요약으로 컨텍스트 압축 |
| 15:45-16:15 | LangGraph 메모리 | `2.langchain/5.memory/7.1_langgraph_memory.py`, `2.langchain/5.memory/7.2_langgraph_memory2_summary.py` | LangGraph 기반 최신 메모리 패턴 |
| 16:15-17:00 | 종합 실습 | `2.langchain/5.memory/5.4_history_chatbot_cli.py` | 학습 내용을 결합한 CLI 챗봇 완성 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-community langgraph
```

## 참고 자료
- `2.langchain/1.llm_models/` — 모델 호출
- `2.langchain/2.prompts/` — 프롬프트 템플릿
- `2.langchain/3.structured_output/` — 출력 파서
- `2.langchain/4.chaining/` — LCEL 체이닝
- `2.langchain/5.memory/` — 메모리 관리
