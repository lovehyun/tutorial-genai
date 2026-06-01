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
| 10:45-11:15 | 프롬프트 템플릿 기초 | `2.langchain/2.prompts/1.basic/1.1_template_chat.py`, `2.langchain/2.prompts/1.basic/1.2_template_invoke_chat.py` | PromptTemplate 생성과 invoke |
| 11:15-12:00 | 프롬프트 체이닝 | `2.langchain/2.prompts/2.chat_templates/2.2_template_chat_chaining.py`, `2.langchain/4.chaining/0.legacy(instruct)/1.4_template_chaining_lambda_instruct.py` | 프롬프트 간 체이닝, Lambda 활용 |
| 13:00-13:30 | Chat 프롬프트 | `2.langchain/2.prompts/2.chat_templates/2.1_template_chat.py`, `2.langchain/2.prompts/2.chat_templates/2.2_template_chat_chaining.py` | ChatPromptTemplate와 역할 분리 |
| 13:30-14:00 | 실전 프롬프트 (요약/번역) | `2.langchain/5.tasks/1.summarization_chat.py`, `2.langchain/5.tasks/2.translation_chat.py` | 요약, 번역 프롬프트 패턴 |
| 14:00-14:30 | 실전 프롬프트 (이메일/SQL) | `2.langchain/5.tasks/3.emailgeneration_chat.py`, `2.langchain/5.tasks/4.sqlgeneration_chat.py` | 이메일 생성, SQL 생성 |
| 14:45-15:15 | Output Parser | `2.langchain/3.structured_output/1.str_output_parser.py`, `2.langchain/3.structured_output/3.pydantic_parser.py` | 문자열, Pydantic 파서 |
| 15:15-15:45 | Structured Output | `2.langchain/3.structured_output/4.with_structured_output.py` | with_structured_output 메서드 |
| 15:45-16:15 | LCEL 체이닝 기초 | `2.langchain/4.chaining/1.basics/1.1_basic_chain.py`, `2.langchain/4.chaining/1.basics/1.2_basic_chain_with_lambda.py` | 파이프 연산자(|) 기반 LCEL |
| 16:15-17:00 | RunnableLambda | `2.langchain/4.chaining/2.runnablelambda/2.1_runnablelambda_basic.py`, `2.langchain/4.chaining/2.runnablelambda/2.4_runnablelambda_pii_mask.py` | 커스텀 함수를 체인에 삽입 |

### Day 2: 고급 체이닝 · 메모리 · 종합 실습

| 시간 | 주제 | 실습 파일 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 | — | 전일 내용 요약, Q&A |
| 09:30-10:00 | RunnablePassthrough | `2.langchain/4.chaining/3.runnablepassthrough/3.1_passthrough_basic.py`, `2.langchain/4.chaining/3.runnablepassthrough/3.2_passthrough_chain.py` | 입력 데이터 통과 패턴 |
| 10:00-10:30 | 병렬 체이닝 | `2.langchain/4.chaining/4.runnableparallel/4.1_parallel_basic.py`, `2.langchain/4.chaining/6.runnablemap/6.1_runnablemap_basic.py` | RunnableParallel, RunnableMap |
| 10:45-11:15 | 프로덕션 패턴 | `2.langchain/4.chaining/10.production/10.1_production_fallback_retry.py` | Fallback, Retry 전략 |
| 11:15-12:00 | Flask 연동 | `2.langchain/1.llm_models/2.1_openai_flask_api.py`, `2.langchain/1.llm_models/2.2_openai2_flask_fe.py` | LangChain + Flask API 서버 |
| 13:00-13:30 | 메모리 없는 대화 | `2.langchain/6.memory/1.nomemory/1.1_langchain_review.py`, `2.langchain/6.memory/1.nomemory/1.2_nomemory.py` | 메모리 없는 챗봇의 한계 체험 |
| 13:30-14:00 | 메모리 기본 | `2.langchain/6.memory/2.storage/2.1_inmemory.py`, `2.langchain/6.memory/2.storage/2.2_file.py` | 인메모리 메모리, 파일 저장 |
| 14:00-14:30 | SQLite 메모리 | `2.langchain/6.memory/2.storage/2.3_sqlite.py` | SQLite 기반 영구 메모리 |
| 14:45-15:15 | 히스토리 & 세션 | `2.langchain/6.memory/3.sessions/3.1_history.py`, `2.langchain/6.memory/3.sessions/3.2_history_session.py` | ChatMessageHistory, 세션 관리 |
| 15:15-15:45 | 히스토리 요약 | `2.langchain/6.memory/4.compression/4.2_summary_basic.py`, `2.langchain/6.memory/4.compression/4.3_summary_session.py` | 대화 요약으로 컨텍스트 압축 |
| 15:45-16:15 | LangGraph 메모리 | `2.langchain/6.memory/6.langgraph/6.1_memory_saver.py`, `2.langchain/6.memory/6.langgraph/6.2_with_summary.py` | LangGraph 기반 최신 메모리 패턴 |
| 16:15-17:00 | 종합 실습 | `2.langchain/6.memory/4.compression/4.5_chatbot_cli.py` | 학습 내용을 결합한 CLI 챗봇 완성 |

## 환경 설정

```bash
pip install langchain langchain-openai langchain-community langgraph
```

## 이론 교안

| 교안 | 내용 |
|------|------|
| `0.docs/05_genai_advanced/07_langchain_lcel.md` | LangChain LCEL 아키텍처 |
| `0.docs/05_genai_advanced/04_prompt_engineering_code.md` | 프롬프트 엔지니어링 코드 실전 |
| `0.docs/05_genai_advanced/05_context_engineering.md` | 컨텍스트 엔지니어링 |

## 참고 자료
- `2.langchain/1.llm_models/` — 모델 호출
- `2.langchain/2.prompts/` — 프롬프트 템플릿
- `2.langchain/3.structured_output/` — 출력 파서
- `2.langchain/4.chaining/` — LCEL 체이닝
- `2.langchain/6.memory/` — 메모리 관리
