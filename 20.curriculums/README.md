# 생성형 AI 교육 커리큘럼 카탈로그

> 본 리포지토리의 400+ 예제 파일을 기반으로 구성한 난이도별 교육 과정입니다.
> 각 과정은 기존 예제 코드를 활용하며, 별도의 새 코드를 작성하지 않습니다.

## 과정 요약

| Level | # | 과정명 | 기간 | 시간 | 핵심 영역 |
|-------|---|--------|------|------|-----------|
| 입문 | 1 | [생성형 AI API 첫걸음](1.intro/1.genai_api_first_step/) | 1일 | 8h | OpenAI/Gemini REST → SDK → Vision → Streaming |
| 입문 | 2 | [나만의 챗봇 만들기](1.intro/2.chatbot_from_scratch/) | 2일 | 16h | 챗봇 점진 구축 (UI → 히스토리 → SQLite → 세션 → 토론봇) |
| 입문 | 3 | [LangChain 핵심 마스터](1.intro/3.langchain_essentials/) | 2일 | 16h | 모델 / 프롬프트 / 파서 / LCEL / 메모리 |
| 입문 | 4 | [멀티모달 AI 입문](1.intro/4.multimodal_ai_intro/) | 1일 | 8h | DALL-E / Whisper / Vision / WebRTC |
| 입문 | 5 | [로컬 LLM 빠르게 시작하기](1.intro/5.local_llm_quickstart/) | 1일 | 8h | Transformers / Ollama / GPT4All / 한국어 NLP |
| 중급 | 1 | [RAG 마스터클래스](2.intermediate/1.rag_masterclass/) | 3일 | 24h | 임베딩 → FAISS → ChromaDB → RAG 웹앱 → Agentic RAG |
| 중급 | 2 | [AI 에이전트 개발](2.intermediate/2.agent_development/) | 3일 | 24h | 도구 / Wikipedia / ArXiv / Human Agent / 복합 Agent |
| 중급 | 3 | [LangGraph & Agentic 패턴](2.intermediate/3.langgraph_and_patterns/) | 2일 | 16h | StateGraph / 순환 / Self-Correction / 5대 패턴 |
| 중급 | 4 | [멀티 프로바이더 통합](2.intermediate/4.multi_provider_integration/) | 2일 | 16h | Claude / Gemini + LangChain 통합 + 코드리뷰 앱 |
| 고급 | 1 | [MCP 프로토콜 심화](3.advanced/1.mcp_protocol_deep_dive/) | 3일 | 24h | MCP 서버/클라이언트/에이전트/LangChain 브릿지/Desktop |
| 고급 | 2 | [프로덕션 LLM 앱](3.advanced/2.production_llm_apps/) | 3일 | 24h | Flask 앱 6종 (영어학습/리뷰요약/코드리뷰/시험채점 등) |
| 고급 | 3 | [모델 최적화 & MLOps](3.advanced/3.model_optimization_mlops/) | 2일 | 16h | Transformer 내부 / 양자화 / 가지치기 / 지식증류 / 배포 |
| 고급 | 4 | [Agentic 아키텍처 설계](3.advanced/4.agentic_architecture/) | 5일 | 40h | LangGraph 심화 + 5대 패턴 + MCP + 멀티에이전트 + 캡스톤 |
| 고급 | 5 | [풀스택 AI 캡스톤](3.advanced/5.fullstack_ai_capstone/) | 5일 | 40h | 매일 2~3개 프로젝트 직접 구축 + 자유 캡스톤 + 발표 |

**총 14개 과정 · 35일 · 280시간**

---

## 레벨별 설명

### 입문 (Intro) — 7일 · 56시간

프로그래밍 경험은 있지만 생성형 AI를 처음 접하는 학습자를 위한 과정입니다. REST API 호출부터 시작해 SDK, 챗봇 UI, LangChain 기초, 멀티모달, 로컬 LLM까지 폭넓게 경험합니다.

- **선수 지식**: Python 기초, pip/venv 사용법
- **학습 성과**: OpenAI/Gemini API 활용, Gradio 챗봇 구현, LangChain LCEL 파이프라인 구축

### 중급 (Intermediate) — 10일 · 80시간

API 호출과 기본 체이닝에 익숙한 학습자가 RAG, 에이전트, LangGraph, 멀티 프로바이더 통합 등 실전 패턴을 학습합니다.

- **선수 지식**: 입문 과정 수료 또는 동등 수준
- **학습 성과**: RAG 파이프라인 구축, 커스텀 에이전트 개발, LangGraph 워크플로우 설계

### 고급 (Advanced) — 18일 · 144시간

프로덕션 수준의 LLM 애플리케이션 개발, 모델 최적화, MCP 프로토콜 심화, 아키텍처 설계를 다룹니다.

- **선수 지식**: 중급 과정 수료 또는 동등 수준
- **학습 성과**: MCP 서버/클라이언트 구축, Flask 프로덕션 앱, 모델 최적화, 멀티에이전트 시스템 설계

---

## 선수 과목 관계도

```
입문 1. 생성형 AI API 첫걸음
├── 입문 2. 나만의 챗봇 만들기
├── 입문 4. 멀티모달 AI 입문
├── 입문 5. 로컬 LLM 빠르게 시작하기
└── 입문 3. LangChain 핵심 마스터
    ├── 중급 1. RAG 마스터클래스
    │   └── 고급 2. 프로덕션 LLM 앱
    ├── 중급 2. AI 에이전트 개발
    │   └── 중급 3. LangGraph & Agentic 패턴
    │       └── 고급 4. Agentic 아키텍처 설계
    ├── 중급 4. 멀티 프로바이더 통합
    │   └── 고급 1. MCP 프로토콜 심화
    └── 고급 5. 풀스택 AI 캡스톤 (중급 전체 수료 권장)

입문 5. 로컬 LLM 빠르게 시작하기
└── 고급 3. 모델 최적화 & MLOps
```

---

## 일정 구성 기준

- 1일 = **8시간** (09:00–17:00)
- 점심시간: 12:00–13:00 (1시간)
- 휴식: 10:30–10:45, 14:30–14:45 (각 15분)
- 실질 교육 시간: **6.5시간/일**

---

## 주요 참조 디렉토리

| 디렉토리 | 파일 수 | 내용 |
|----------|--------|------|
| `1.openai/` | 49 | OpenAI API, 챗봇, RAG, 스트리밍, 멀티모달 |
| `2.langchain/` | 90 | LLM 모델, 프롬프트, 체이닝, 메모리, RAG, 에이전트, LangGraph |
| `3.local/` | 57 | Transformers, HuggingFace, Ollama, GPT4All, 한국어 LLM |
| `4.anthropic/` | 58 | Claude API, LangChain 통합, MCP 프로토콜 |
| `7.google/` | 10 | Gemini API, 멀티모달, LangChain 통합 |
| `9.study/` | 23 | Transformer 내부, BERT, 토크나이저, 임베딩, 어텐션 |
| `10.project/` | 82 | Flask 앱 프로젝트 (챗봇, 영어학습, 코드리뷰, 시험채점 등) |
