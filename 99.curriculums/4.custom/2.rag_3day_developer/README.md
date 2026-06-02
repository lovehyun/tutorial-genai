# 3일 완성 RAG 개발자 과정

> 이 한 문서에 **커리큘럼(시간표) + 이론 요약 + 모든 기본 코드 스니펫**을 모두 담았습니다.
> 이론은 `0.docs/`에서, 코드는 `1.openai/`·`2.langchain/`의 실제 예제에서 발췌했습니다.

## 과정 정보
- **기간**: 3일 (총 24시간, 하루 8시간)
- **난이도**: 입문 → 중급
- **대상**: 파이썬 기본 문법을 알고, 생성형 AI/LLM API로 문서 기반 챗봇(RAG)을 만들어보고 싶은 개발자
- **선수 과목**: 없음 (파이썬 기초 권장)
- **목표 산출물**: 내 문서를 업로드하면 답해주는 RAG 기반 QA 웹서비스

## 학습 목표
1. 생성형 AI/LLM의 동작 원리를 이해하고 REST API와 SDK로 챗봇을 만들 수 있다
2. 프롬프트 엔지니어링과 컨텍스트 엔지니어링의 원리를 이해하고 적용할 수 있다
3. LangChain의 핵심 구성요소(Model·Prompt·Parser·Chain·Memory)로 LLM 앱을 구조화할 수 있다
4. 임베딩·벡터 검색의 원리를 이해하고 RAG 파이프라인과 웹서비스를 구축할 수 있다

---

## 시간표 한눈에 보기 (오전 / 오후)

| 구분 | 오전 (09:00–12:00) | 오후 (13:00–17:00) |
|------|---------------------|---------------------|
| **Day 1**<br>API·프롬프트 | 강사소개·OT / 생성형 AI 이론 기초 / REST API 요청·응답 | SDK·멀티턴 챗봇 / 프롬프트 엔지니어링 / 컨텍스트 엔지니어링 |
| **Day 2**<br>LangChain | LangChain 개요·모델 / 프롬프트 템플릿 / Output Parser | LCEL 체이닝 / 메모리 / 종합 실습(메모리 챗봇) |
| **Day 3**<br>RAG·웹 | RAG 개요·임베딩 / FAISS·청킹 / 첫 RAG 체인 | 벡터스토어 영속화 / 표준·대화형 RAG / 웹서비스·종합 프로젝트 |

> 시간표: 09:00–17:00 / 점심 12:00–13:00 / 휴식 10:30–10:45, 14:30–14:45

---

## 상세 커리큘럼

### Day 1: 생성형 AI 기초 · API · 프롬프트/컨텍스트 엔지니어링

**오전 (09:00–12:00) — 이론과 REST API 기초**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 09:00-09:40 | 강사 소개 & OT | — | 과정 소개, 산출물 미리보기, 개발 환경(.env, API 키) 설정 |
| 09:40-10:30 | 생성형 AI 이론 기초 | `0.docs/00_OT/05_generative_ai_intro.md` | AI/ML/DL/GenAI/LLM, "다음 단어 예측", Transformer, 토큰·컨텍스트 윈도우 |
| 10:45-11:15 | REST API 첫 호출 | `1.openai/1.intro/1.restapi_hello.py`, `1.openai/1.intro/2.restapi_content.py` | Chat Completions 엔드포인트, JSON 응답 구조, role(system/user/assistant) |
| 11:15-12:00 | 파라미터 & 함수화 | `1.openai/1.intro/3.restapi_params.py`, `1.openai/1.intro/4.restapi_chat.py` | temperature·max_tokens, 예외 처리, 대화 루프 |

**오후 (13:00–17:00) — SDK 챗봇과 프롬프트/컨텍스트 엔지니어링**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 13:00-13:30 | OpenAI SDK | `1.openai/1.intro/11.sdk_new.py` | REST vs SDK 비교, `client.chat.completions.create()` |
| 13:30-14:10 | 멀티턴 & 대화 히스토리 | `1.openai/1.intro/13.chat_multiturn.py`, `1.openai/3.chatbot2_history/app3_history.py` | messages 누적으로 맥락 유지, system prompt 적용 |
| 14:10-14:30 | 히스토리 길이 제한 | `1.openai/3.chatbot2_history/app4_historylimit.py` | 토큰 절약을 위한 최근 N개 유지 |
| 14:45-15:30 | 프롬프트 엔지니어링 개요 | `0.docs/01_genai_intro/04_prompt_engineering.md` | Zero/Few-shot, CoT, ReAct, CRAFT 공식 |
| 15:30-16:15 | 컨텍스트 엔지니어링 | `0.docs/01_genai_intro/05_so_what_now.md`, `0.docs/05_genai_advanced/05_context_engineering.md` | 컨텍스트 윈도우 6요소, 토큰 관리, "AI는 천재 인턴" |
| 16:15-17:00 | Day 1 실습 & 정리 | `1.openai/1.intro/4.restapi_chat.py` | 나만의 system prompt CLI 챗봇 완성, Q&A |

### Day 2: LangChain으로 구조화하기

**오전 (09:00–12:00) — 모델 · 프롬프트 · 파서**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 1 복습 & LangChain 개요 | `0.docs/05_genai_advanced/07_langchain_lcel.md` | 왜 LangChain인가, 아키텍처 한눈에 |
| 09:30-10:10 | 모델 호출 | `2.langchain/1.llm_models/1.2_openai2_chat.py` | `ChatOpenAI`, 문자열 vs 메시지 객체(System/Human) |
| 10:10-10:30 | 프롬프트 템플릿 | `2.langchain/2.prompts/1.basic/1.1_template_chat.py` | `ChatPromptTemplate`, system+user 역할 분리 |
| 10:45-11:15 | 프롬프트 invoke & 실전 | `2.langchain/2.prompts/1.basic/1.2_template_invoke_chat.py`, `2.langchain/5.tasks/1.summarization_chat.py` | invoke, 요약/번역 프롬프트 패턴 |
| 11:15-12:00 | Output Parser | `2.langchain/3.structured_output/1.str_output_parser.py`, `2.langchain/3.structured_output/4.with_structured_output.py` | Str/List 파서, Pydantic 구조화 출력 |

**오후 (13:00–17:00) — 체이닝 · 메모리 · 종합 실습**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 13:00-13:40 | LCEL 체이닝 기초 | `2.langchain/4.chaining/1.basics/1.1_basic_chain.py` | 파이프(\|) 연산자: `prompt \| llm \| parser` |
| 13:40-14:30 | RunnableLambda / Passthrough | `2.langchain/4.chaining/2.runnablelambda/2.1_runnablelambda_basic.py`, `2.langchain/4.chaining/3.runnablepassthrough/3.1_passthrough_basic.py` | 함수 삽입, 입력 보존하며 키 누적 |
| 14:45-15:30 | 메모리 기초 | `2.langchain/6.memory/1.nomemory/1.2_nomemory.py`, `2.langchain/6.memory/2.storage/2.1_inmemory.py` | 메모리 없는 한계 체험 → InMemory 히스토리 |
| 15:30-16:00 | 세션 & 영속 메모리 | `2.langchain/6.memory/2.storage/2.3_sqlite.py`, `2.langchain/6.memory/3.sessions/3.2_history_session.py` | SQLite 영구 저장, session_id별 분리 |
| 16:00-17:00 | 종합 실습 | `2.langchain/6.memory/4.compression/4.5_chatbot_cli.py` | 메모리 + 요약을 결합한 CLI 챗봇 완성 |

### Day 3: RAG 챗봇과 웹서비스

**오전 (09:00–12:00) — 임베딩 · FAISS · 청킹 · 첫 RAG 체인**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 09:00-09:30 | Day 2 복습 & RAG 개요 | `0.docs/04_database/11_vector_databases.md` | 왜 RAG인가, 할루시네이션, "오픈북 시험" 비유 |
| 09:30-10:10 | 임베딩 이해 | `2.langchain/7.RAG/1.basics/1.1_embeddings_intro.py` | 텍스트→벡터, 코사인 유사도로 의미 거리 |
| 10:10-10:30 | FAISS 기본 RAG | `1.openai/7.rag/1.rag_basic.py` | 문서→임베딩→FAISS 검색→GPT 응답 파이프라인 |
| 10:45-11:15 | 텍스트 전처리 · 청킹 | `2.langchain/7.RAG/2.loaders/2.3_chunking.py` | chunk_size·overlap, splitter 3종 비교 |
| 11:15-12:00 | 첫 RAG 체인 | `2.langchain/7.RAG/1.basics/1.3_first_rag.py`, `2.langchain/7.RAG/1.basics/1.4_rag_lcel_chain.py` | InMemoryVectorStore + LCEL 검색 체인 |

**오후 (13:00–17:00) — 영속화 · 대화형 RAG · 웹서비스**

| 시간 | 주제 | 실습/교안 | 설명 |
|------|------|-----------|------|
| 13:00-13:40 | 벡터스토어 영속화 | `2.langchain/7.RAG/3.vectorstore/3.1_persist.py` | ChromaDB persist — 재실행 시 임베딩 비용 0 |
| 13:40-14:30 | 표준 RAG 체인 | `2.langchain/7.RAG/4.rag_chain/4.1_standard_chain.py` | `RunnablePassthrough.assign`, top-k 검색, 출처 |
| 14:45-15:15 | 대화형 RAG | `2.langchain/7.RAG/5.conversational/5.3_full_conversational_rag.py` | history-aware retriever, 후속 질문("그거") 처리 |
| 15:15-16:00 | RAG 웹앱 구축 | `2.langchain/7.RAG/8.web_app/1.minimal/app.py` | Flask: `/upload`(문서 업로드) + `/ask`(질문 응답) |
| 16:00-17:00 | 종합 프로젝트 & 발표 | — | 나만의 문서 QA 웹서비스 완성, 결과 발표 |

---

## 환경 설정

```bash
# Day 1 (OpenAI API 기초)
pip install openai requests python-dotenv

# Day 2 (LangChain)
pip install langchain langchain-openai langchain-community

# Day 3 (RAG)
pip install faiss-cpu numpy chromadb langchain-chroma langchain-text-splitters pypdf flask
```

`.env` 파일에 API 키를 둡니다.

```
OPENAI_API_KEY=sk-...
```

## 이론 교안 (0.docs)

| 교안 | 내용 | 사용 시점 |
|------|------|-----------|
| `0.docs/00_OT/05_generative_ai_intro.md` | 생성형 AI/LLM 동작 원리 | Day 1 |
| `0.docs/02_web_basics/05_http_protocol.md` | HTTP 요청/응답 구조 | Day 1 |
| `0.docs/03_python_webdev/13_external_api_and_gpt.md` | OpenAI API 호출, 토큰·비용 | Day 1 |
| `0.docs/01_genai_intro/04_prompt_engineering.md` | 프롬프트 기법의 진화 | Day 1 |
| `0.docs/01_genai_intro/05_so_what_now.md` | 컨텍스트 엔지니어링 | Day 1 |
| `0.docs/05_genai_advanced/05_context_engineering.md` | 컨텍스트 엔지니어링 코드 실전 | Day 1 |
| `0.docs/05_genai_advanced/07_langchain_lcel.md` | LangChain LCEL 아키텍처 | Day 2 |
| `0.docs/04_database/11_vector_databases.md` | 임베딩·유사도·ANN·RAG 이론 | Day 3 |
| `0.docs/05_genai_advanced/06_rag_system.md` | RAG 시스템 전체 파이프라인 | Day 3 |

## 참고 자료 (예제 디렉토리)
- `1.openai/1.intro/` — REST API → SDK 진행 단계
- `1.openai/3.chatbot2_history/` — 대화 히스토리 관리
- `1.openai/7.rag/` — FAISS 기반 RAG 기초
- `2.langchain/` — LangChain 전체 (모델·프롬프트·파서·체인·메모리·RAG)
- `2.langchain/7.RAG/8.web_app/` — RAG 웹앱 단계별 빌드업

---
---

# 교재 — 이론 요약 + 모든 기본 코드 스니펫

> 각 스니펫 상단에 원본 파일 경로를 표시했으니, 더 자세한 주석은 원본을 참고하세요.

## 교재 목차
- **Day 1 — 생성형 AI 기초 · API · 프롬프트/컨텍스트 엔지니어링**
  1. 생성형 AI 이론 기초
  2. REST API 요청과 응답
  3. OpenAI SDK & 멀티턴 대화
  4. 프롬프트 엔지니어링 개요
  5. 컨텍스트 엔지니어링
- **Day 2 — LangChain으로 구조화하기**
  6. LangChain 개요와 모델
  7. 프롬프트 템플릿
  8. Output Parser
  9. LCEL 체이닝
  10. 메모리
- **Day 3 — RAG 챗봇과 웹서비스**
  11. 임베딩과 유사도
  12. FAISS 기본 RAG
  13. 텍스트 전처리(청킹)
  14. LangChain RAG 체인
  15. 벡터스토어 영속화와 표준 체인
  16. 대화형 RAG
  17. RAG 웹서비스
- **부록** — 환경 설정 / 패키지 / 예제 매핑

---

# [Day 1] 생성형 AI 기초 · API · 프롬프트/컨텍스트 엔지니어링

## 1. 생성형 AI 이론 기초
> 교안: `0.docs/00_OT/05_generative_ai_intro.md`

### 1.1 AI의 큰 그림
```
AI(인공지능) ⊃ ML(머신러닝) ⊃ DL(딥러닝) ⊃ 생성형 AI ⊃ LLM
```
| 개념 | 정의 | 예시 |
|------|------|------|
| **AI** | 인간 지능을 모방하는 모든 기술 | 체스 AI, 자율주행 |
| **ML** | 데이터에서 패턴을 학습 | 스팸 필터, 추천 |
| **딥러닝** | 신경망 기반 머신러닝 | 이미지 인식, 번역 |
| **생성형 AI** | **새로운 콘텐츠**를 만들어냄 | 글·그림·음악·코드 |
| **LLM** | 텍스트 생성에 특화된 초거대 모델 | ChatGPT, Claude, Gemini |

- **판별형(Discriminative)**: "이것은 고양이인가?" → 분류/예측
- **생성형(Generative)**: "고양이를 그려줘" → 새로운 결과물 생성

### 1.2 LLM은 어떻게 동작하는가 — "다음 단어 예측"
> 주어진 텍스트 다음에 올 가장 적절한 토큰을 확률적으로 예측한다.

```
입력: "오늘 날씨가 정말"
→ "좋다"(35%) | "덥다"(25%) | "춥다"(15%) | ...
```
이 단순한 원리를 **수조 개 파라미터 + 인터넷 규모 데이터**로 스케일업하면
"이해하고 생각하는 것처럼" 보이는 결과가 나옵니다.

### 1.3 Transformer 아키텍처 (2017, "Attention Is All You Need")
```
입력 텍스트 → 토큰화 → 임베딩 → Self-Attention(★ 단어 간 관계 파악)
            → Feed Forward → 다음 토큰 확률 분포
```
- **Self-Attention**: 문맥에 따라 단어 의미를 동적으로 파악
  - "그 **은행**에서 돈을 인출했다" → ("돈","인출")과의 관계 → 금융 기관

### 1.4 꼭 알아야 할 용어
| 용어 | 설명 | 비유 |
|------|------|------|
| **파라미터** | 모델이 학습한 가중치(지식의 단위) | 뇌의 시냅스 |
| **토큰** | 텍스트 처리 최소 단위 | 한글 1글자 ≈ 2~3토큰 |
| **컨텍스트 윈도우** | 한 번에 처리 가능한 최대 토큰 수 | 작업 기억(Working Memory) |
| **Temperature** | 출력 랜덤성(0=확정적, 높을수록 창의적) | 모험심의 정도 |
| **할루시네이션** | 사실이 아닌 것을 사실처럼 생성 | 그럴듯한 거짓말 |
| **RAG** | 외부 문서를 검색해 답변에 활용 | 오픈북 시험 |

### 1.5 한계와 주의점
| 한계 | 대응 |
|------|------|
| 할루시네이션 | 중요한 정보는 반드시 검증 |
| 최신 정보 부족 | **RAG**, 웹 검색 연동 |
| 수학/논리 약점 | 코드 실행 도구 연동 |
| 보안/개인정보 | 민감 정보 입력 주의 |

---

## 2. REST API 요청과 응답
> 예제: `1.openai/1.intro/` · 교안: `0.docs/02_web_basics/05_http_protocol.md`, `0.docs/03_python_webdev/13_external_api_and_gpt.md`

핵심: 우리 프로그램이 OpenAI의 `POST /v1/chat/completions` 엔드포인트에
**messages 배열**을 보내면, **JSON 응답**이 돌아옵니다.

### 2.1 가장 단순한 호출 — 응답 구조 직접 보기
> `1.openai/1.intro/1.restapi_hello.py`
```python
import os, requests
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
openai_api_key = os.getenv('OPENAI_API_KEY')

response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    },
    json={
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'user', 'content': '안녕, 챗봇!'},
        ],
    },
)
print(response.json())   # 답변은 choices[0].message.content 안에 있다
```

### 2.2 답변만 추출 + 역할(role)
> `1.openai/1.intro/2.restapi_content.py`

메시지의 3가지 역할:
- `system`: 챗봇의 정체성·말투·규칙 (대화 시작 전 1회)
- `user`: 사용자의 질문/요청
- `assistant`: 모델의 지난 답변 (멀티턴에서 다시 넣음)

```python
response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={'Content-Type': 'application/json',
             'Authorization': f'Bearer {openai_api_key}'},
    json={
        'model': 'gpt-4o-mini',
        'messages': [
            {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다.'},
            {'role': 'user',   'content': '안녕, 챗봇!'},
        ],
    },
)
data = response.json()
answer = data['choices'][0]['message']['content']   # 답변 텍스트만 추출
print('챗봇:', answer)
```

### 2.3 응답을 조절하는 파라미터
> `1.openai/1.intro/3.restapi_params.py`
```python
json={
    'model': 'gpt-4o-mini',
    'messages': [...],
    'temperature': 0.7,        # 창의성 (0.0 정확 ~ 2.0 창의)
    'max_tokens': 100,         # 응답 최대 토큰 수(길이 제한)
    'top_p': 0.9,              # 확률 상위 토큰만 선택
    'frequency_penalty': 0.5,  # 같은 단어 반복 억제 (-2.0~2.0)
    'presence_penalty': 0.6,   # 새로운 주제 도입 장려 (-2.0~2.0)
}
```

### 2.4 함수화 + 예외 처리 + 대화 루프 (REST 완성형)
> `1.openai/1.intro/4.restapi_chat.py`
```python
system_prompt = '당신은 친절한 AI 도우미입니다.'

def ask_chatgpt(user_input):
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={'Content-Type': 'application/json',
                     'Authorization': f'Bearer {openai_api_key}'},
            json={
                'model': 'gpt-4o-mini',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_input},
                ],
                'temperature': 0.7, 'max_tokens': 200,
            },
        )
        response.raise_for_status()   # 4xx/5xx면 예외 발생
        return response.json()['choices'][0]['message']['content']
    except Exception as error:
        print('API 요청 중 오류 발생:', str(error))
        return '응답을 가져오는 도중 오류가 발생했습니다.'

if __name__ == '__main__':
    print('챗봇과 대화를 시작합니다. (종료: exit)')
    while True:
        user_input = input('\n나: ').strip()
        if user_input.lower() == 'exit':
            break
        print('챗봇:', ask_chatgpt(user_input))
```
> ⚠️ 매 호출이 독립적이라 아직 **대화 기억이 없다** → 3.2에서 해결.

---

## 3. OpenAI SDK & 멀티턴 대화
> 예제: `1.openai/1.intro/`, `1.openai/3.chatbot2_history/`

### 3.1 신버전 SDK (v1.x) — 현재 표준
> `1.openai/1.intro/11.sdk_new.py`

REST와 결과는 같지만 코드가 훨씬 간결합니다.
```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다.'},
        {'role': 'user',   'content': '안녕, 챗봇!'},
    ],
)
# 객체 속성으로 접근 (REST의 ['choices'][0]['message']['content']와 비교)
print('챗봇:', response.choices[0].message.content)
```

### 3.2 멀티턴 — messages 리스트에 대화를 누적
> `1.openai/1.intro/13.chat_multiturn.py`

멀티턴의 핵심: 이전 대화를 함께 보내면 맥락이 이어집니다.
모델의 지난 답변은 `assistant` 역할로 다시 넣습니다.
```python
messages = [
    {'role': 'system', 'content': '당신은 친절한 AI 도우미입니다.'},
]

def chat(user_input):
    messages.append({'role': 'user', 'content': user_input})      # 1) 사용자 메시지 추가
    response = client.chat.completions.create(                    # 2) 전체 대화를 전송
        model='gpt-4o-mini', messages=messages,
    )
    answer = response.choices[0].message.content
    messages.append({'role': 'assistant', 'content': answer})     # 3) 답변도 누적 → 다음 턴에서 기억
    return answer

for q in ['대한민국의 수도는 어디야?', '그 도시의 인구는 얼마야?']:
    print('나:', q)
    print('챗봇:', chat(q))   # 2번째 질문의 '그 도시'를 맥락으로 이해
```

### 3.3 웹 챗봇으로 — 히스토리 관리
> `1.openai/3.chatbot2_history/app3_history.py` (인메모리 히스토리)
> `1.openai/3.chatbot2_history/app4_historylimit.py` (최근 N개만 유지 → 토큰 절약)

핵심 아이디어는 3.2와 동일합니다. 서버가 사용자별 `messages` 리스트를 들고
계속 누적하며, 너무 길어지면 **최근 N개만 유지**해 토큰 비용을 아낍니다.
```python
# 히스토리 길이 제한의 핵심 패턴
MAX_TURNS = 10
messages = messages[:1] + messages[-(MAX_TURNS * 2):]   # system 1개 + 최근 대화만
```

---

## 4. 프롬프트 엔지니어링 개요
> 교안: `0.docs/01_genai_intro/04_prompt_engineering.md`

> **프롬프트 엔지니어링** = AI에게 원하는 결과를 얻기 위해 입력을 설계하는 기술.
> 같은 모델도 "어떻게 질문하느냐"에 따라 결과 품질이 천지차이.

### 4.1 기법의 진화 (요약)
| 기법 | 시기 | 핵심 아이디어 | 적합 상황 |
|------|------|--------------|-----------|
| **Zero-Shot** | 2020~ | 예시 없이 바로 질문 | 간단한 질문/번역 |
| **Few-Shot** | 2022 | 2~3개 예시 제공 | 특정 형식 필요 |
| **CoT** | 2022.01 | "단계별로 생각해봐" | 수학·논리 추론 |
| **Zero-Shot CoT** | 2022.05 | "Let's think step by step" 한 줄 | 범용 추론 향상 |
| **ReAct** | 2022.10 | 생각 → 행동(도구) → 관찰 반복 | 최신 정보, 사실 확인 |
| **ToT** | 2023.05 | 여러 경로를 트리로 탐색 | 복잡한 계획/전략 |
| **Self-Consistency / Reflexion** | 2023 | 다수결 / 자기 검증·수정 | 정확도 중요 작업 |
| **Agentic** | 2024~ | 목표만 주면 스스로 계획·실행 | 멀티스텝 자율 작업 |
| **Meta-Prompting** | 2025~ | 프롬프트를 만드는 프롬프트 | 최적 결과 추구 |

> Zero-Shot CoT 효과: MultiArith 벤치마크에서 정답률 17% → 79% (4.6배).

### 4.2 Few-Shot 예시
```
다음 예시처럼 감정을 분석해줘:
문장: "정말 화가 난다" → 감정: 분노
문장: "너무 슬프다"   → 감정: 슬픔
문장: "오늘 기분이 좋아!" → 감정: 기쁨

문장: "시험에 떨어졌어" → 감정:
```

### 4.3 황금 공식: CRAFT
```
C - Context (맥락): 상황을 설명한다
R - Role    (역할): 전문가 역할을 부여한다
A - Action  (행동): 무엇을 해야 하는지 구체적으로 지시
F - Format  (형식): 출력 형식을 지정한다
T - Tone    (톤):   어조와 스타일을 지정한다
```
**나쁜 프롬프트**: `파이썬 코드 짜줘`
**좋은 프롬프트(CRAFT)**:
```
[역할] 너는 10년차 Python 백엔드 개발자야.
[맥락] Flask로 REST API를 만들고 있어.
[지시] 회원가입 엔드포인트(POST /api/register)를 만들어줘.
       입력: email, password, name / 비밀번호 bcrypt 해싱 / 중복 이메일 체크
[형식] 코드에 한국어 주석을 달아줘.
[예시] 요청: {"email":"a@a.com","password":"1234","name":"홍길동"}
```

---

## 5. 컨텍스트 엔지니어링
> 교안: `0.docs/01_genai_intro/05_so_what_now.md`, `0.docs/05_genai_advanced/05_context_engineering.md`

### 5.1 프롬프트 → 컨텍스트 엔지니어링
> "괜찮은 결과"는 누구나 얻지만, "탁월한 결과"는 여전히 잘 물어보는 사람만 얻는다.

| 구분 | 프롬프트 엔지니어링(과거) | 컨텍스트 엔지니어링(현재) |
|------|--------------------------|--------------------------|
| 초점 | "어떻게 질문할까?" | "어떤 정보를 줄까?" |
| 범위 | 프롬프트 텍스트만 | 시스템 프롬프트 + 메모리 + 도구 + 데이터 + 히스토리 |
| 대상 | 한 번의 질문 | 전체 AI 시스템 |
| 비유 | 좋은 질문을 하는 학생 | 좋은 시험 환경을 만드는 교수 |

> Andrej Karpathy: "컨텍스트 엔지니어링은 컨텍스트 윈도우를 채우는 정교한 기술이자 과학."

### 5.2 컨텍스트 윈도우의 6요소
```
컨텍스트 엔지니어링 = 컨텍스트 윈도우를 무엇으로 채울지 설계하는 것

① 시스템 프롬프트  AI의 역할/규칙
② 대화 히스토리    현재 세션 맥락
③ 메모리           과거 대화/사용자 정보
④ 관련 데이터(RAG) 문서·DB·API 결과   ← Day 3의 핵심
⑤ 도구 정의        사용 가능한 외부 도구
⑥ Few-shot 예시    원하는 출력 샘플
+ 사용자 프롬프트   실제 질문
```

### 5.3 핵심 비유: AI는 천재 인턴
```
좋은 상사(=좋은 컨텍스트 엔지니어):
  "이 프로젝트는 이런 배경이고, 고객은 이런 사람들이야.
   이 문서를 참고해서, 이런 형식으로 보고서를 써줘."
  → 훌륭한 결과물

나쁜 상사: "보고서 써" → 인턴이 뭘 써야 할지 모름
```

### 5.4 2026년에 필요한 5가지 원칙
```
1. 맥락을 충분히 제공하라 (AI는 독심술을 못한다)
2. 구체적으로 요청하라     (무엇을, 어떤 형식으로, 어느 수준으로)
3. 역할을 부여하라         ("너는 10년차 개발자야")
4. 복잡한 건 나눠서 시키라 (단계별 진행)
5. 결과를 반드시 검증하라  (AI는 자신있게 틀린다)
```
> 한 줄 요약: **프롬프트 엔지니어링은 죽지 않았다 — 컨텍스트 엔지니어링으로 흡수되었다.**

---

# [Day 2] LangChain으로 구조화하기

## 6. LangChain 개요와 모델
> 예제: `2.langchain/1.llm_models/` · 교안: `0.docs/05_genai_advanced/07_langchain_lcel.md`

**왜 LangChain?** Day 1에서 직접 짠 호출·히스토리·프롬프트 조립을
표준 구성요소(Model·Prompt·Parser·Chain·Memory)로 **재사용 가능하게** 묶어줍니다.

| 클래스 | 모델 타입 | 입력 |
|--------|-----------|------|
| `OpenAI` | Completion(문장 완성) | `str` |
| `ChatOpenAI` | Chat(대화형) | 메시지 리스트(System/Human/AI) |

### 6.1 모델 호출 세 가지 형태
> `2.langchain/1.llm_models/1.2_openai2_chat.py`
```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(dotenv_path='../.env')

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.9)

# (1) 문자열을 그대로 — 내부적으로 HumanMessage로 변환, 반환은 AIMessage
result = llm.invoke("아케이드 게임 회사 이름 지어줘")
print(result.content)   # .content로 텍스트 추출

# (2) 메시지 객체로 명시적 구성 — Chat 모델의 본래 입력 형식
messages = [
    SystemMessage(content="당신은 창의적인 게임 회사 작명 전문가입니다."),
    HumanMessage(content="아케이드 게임을 만드는 좋은 회사 이름을 지어줘."),
]
print(llm.invoke(messages).content)
```

---

## 7. 프롬프트 템플릿
> 예제: `2.langchain/2.prompts/1.basic/`

변수를 끼워 재사용 가능한 프롬프트를 만듭니다.
> `2.langchain/2.prompts/1.basic/1.1_template_chat.py`
```python
from langchain_core.prompts import ChatPromptTemplate

# 튜플 단축형 — system + user 역할 분리 (권장)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a naming consultant for new companies."),
    ("user",   "Suggest a name for a company that makes {product}."),
])

# 변수 치환 → 메시지 리스트 생성
filled = prompt.format_messages(product="robot toys")
for m in filled:
    print(f"[{m.type}] {m.content}")
```

템플릿 + 모델을 묶어 바로 호출:
> `2.langchain/2.prompts/1.basic/1.2_template_invoke_chat.py`
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
result = llm.invoke(prompt.format_messages(product="electric bikes"))
print(result.content)
```

---

## 8. Output Parser
> 예제: `2.langchain/3.structured_output/`

LLM 응답을 문자열/리스트/구조화 객체로 파싱합니다.
> `2.langchain/3.structured_output/1.str_output_parser.py`
```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, CommaSeparatedListOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# StrOutputParser — AIMessage에서 .content 문자열만 추출
prompt1 = ChatPromptTemplate.from_template("{product}을 만드는 회사 이름을 하나 추천해주세요.")
chain1 = prompt1 | llm | StrOutputParser()
print(chain1.invoke({"product": "웹게임"}))         # <class 'str'>

# CommaSeparatedListOutputParser — 쉼표 응답을 파이썬 리스트로
prompt2 = ChatPromptTemplate.from_template("{topic} 키워드 5개를 쉼표로 나열해주세요.")
chain2 = prompt2 | llm | CommaSeparatedListOutputParser()
print(chain2.invoke({"topic": "인공지능"}))          # <class 'list'>
```

구조화 출력(Pydantic) — 필드/타입을 보장:
> `2.langchain/3.structured_output/4.with_structured_output.py`
```python
from pydantic import BaseModel, Field

class Company(BaseModel):
    name: str = Field(description="회사 이름")
    slogan: str = Field(description="한 줄 슬로건")

structured_llm = llm.with_structured_output(Company)   # LLM 네이티브 함수 호출 방식
result = structured_llm.invoke("친환경 패키징 회사를 하나 제안해줘")
print(result.name, "—", result.slogan)                 # Company 객체로 반환
```

---

## 9. LCEL 체이닝
> 예제: `2.langchain/4.chaining/`

LCEL(LangChain Expression Language): 컴포넌트를 **파이프(`|`)** 로 연결해 하나의 체인으로.

### 9.1 가장 기본 체인 — `prompt | llm | parser`
> `2.langchain/4.chaining/1.basics/1.1_basic_chain.py`
```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 어시스턴트입니다."),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"question": "파이썬이 뭐야? 한 줄로 답해줘."}))
```

### 9.2 RunnableLambda — 체인에 함수 끼우기
> `2.langchain/4.chaining/2.runnablelambda/2.1_runnablelambda_basic.py`
```python
from langchain_core.runnables import RunnableLambda

# 문자열 결과를 다음 체인이 쓸 dict로 변환
to_dict = RunnableLambda(lambda name: {"company_name": name.strip()})
chain = prompt_name | llm | StrOutputParser() | to_dict | prompt_slogan | llm | StrOutputParser()
```

### 9.3 RunnablePassthrough — 입력 보존하며 키 누적
> `2.langchain/4.chaining/3.runnablepassthrough/3.1_passthrough_basic.py`
```python
from langchain_core.runnables import RunnablePassthrough

# 입력 question을 보존하면서 새로운 키를 추가 (RAG에서 context 추가에 그대로 쓰임 → 14장)
chain = RunnablePassthrough.assign(
    answer=lambda x: llm.invoke(x["question"]).content
)
print(chain.invoke({"question": "LCEL이 뭐야?"}))   # {'question': ..., 'answer': ...}
```

---

## 10. 메모리
> 예제: `2.langchain/6.memory/`

### 10.1 메모리 없는 한계 체험
> `2.langchain/6.memory/1.nomemory/1.2_nomemory.py`
> 매 호출이 독립적 → 이전 대화를 기억하지 못함. (Day 1의 멀티턴 문제와 동일)

### 10.2 InMemory 히스토리
> `2.langchain/6.memory/2.storage/2.1_inmemory.py`
```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 한국어 어시스턴트입니다."),
    MessagesPlaceholder("history"),     # ← 누적 메시지가 끼워질 자리
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

history = InMemoryChatMessageHistory()  # 이 한 줄만 storage 종류별로 달라짐(파일/SQLite)

def chat(message):
    answer = chain.invoke({"input": message, "history": history.messages})
    history.add_user_message(message)   # 호출 후 메시지 누적
    history.add_ai_message(answer)
    print(f"Q: {message}\nA: {answer}")

chat("제 이름은 홍길동입니다.")
chat("제 이름을 다시 말해줄래요?")        # 메모리 덕분에 기억함
```

### 10.3 영속·세션·요약
- 파일/SQLite 저장: `FileChatMessageHistory`, `SQLChatMessageHistory`
  > `2.langchain/6.memory/2.storage/2.3_sqlite.py`
- 다중 사용자 분리: `RunnableWithMessageHistory` + `session_id`
  > `2.langchain/6.memory/3.sessions/3.2_history_session.py`
- 토큰 압축(요약): `trim_messages` 또는 자동 요약
  > `2.langchain/6.memory/4.compression/4.5_chatbot_cli.py` (종합 CLI 챗봇)

```python
# 세션별 분리의 핵심 패턴
from langchain_core.runnables.history import RunnableWithMessageHistory

sessions = {}
def get_history(session_id):
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]

with_memory = RunnableWithMessageHistory(
    chain, get_history,
    input_messages_key="input", history_messages_key="history",
)
with_memory.invoke({"input": "안녕"}, config={"configurable": {"session_id": "user-1"}})
```

---

# [Day 3] RAG 챗봇과 웹서비스

## 11. 임베딩과 유사도
> 예제: `2.langchain/7.RAG/1.basics/1.1_embeddings_intro.py` · 교안: `0.docs/04_database/11_vector_databases.md`

### 11.1 왜 RAG인가
- LLM은 학습 시점 이후/사내 문서를 모름 → 모르는 걸 지어냄(할루시네이션)
- **RAG = 오픈북 시험**: 질문에 관련된 문서를 먼저 찾아서 함께 주고 답하게 함

### 11.2 임베딩 = 텍스트를 의미 벡터로
> 의미가 비슷한 문장 = 벡터 공간에서 가까운 점.
```
"파이썬 프로그래밍" → [0.82, -0.31, 0.55, ...]  (1536차원)
"Python 코딩"       → [0.79, -0.28, 0.58, ...]  ← 가까움
"오늘 날씨"         → [-0.12, 0.67, -0.43, ...] ← 멀리
```
| 모델 | 차원 | 특징 |
|------|------|------|
| text-embedding-3-small (OpenAI) | 1536 | 빠르고 저렴, 범용 |
| text-embedding-3-large (OpenAI) | 3072 | 높은 정확도 |
| all-MiniLM-L6-v2 (오픈소스) | 384 | 빠름, 무료 |
| all-mpnet-base-v2 (오픈소스) | 768 | 균형 |

### 11.3 유사도 측정
- **코사인 유사도**: 방향(각도)만 비교, 범위 -1~1, **텍스트 검색 표준**
- 유클리드(L2) 거리: 절대 거리, 0~∞, 작을수록 유사
- 내적: 정규화 시 코사인과 동일

### 11.4 코드 — 임베딩 + 코사인 유사도
> `2.langchain/7.RAG/1.basics/1.1_embeddings_intro.py`
```python
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 단일 문장 → 벡터
vec = embeddings.embed_query("고양이가 소파 위에서 잔다.")
print("벡터 차원:", len(vec))            # 1536

# 여러 문장 벡터화 후 의미 거리 비교
sentences = [
    "고양이가 소파 위에서 잔다.",
    "강아지가 침대에서 자고 있어요.",       # 의미 가까움
    "파이썬은 인기 있는 프로그래밍 언어다.", # 다른 주제
]
vectors = embeddings.embed_documents(sentences)

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        print(f"{cosine_similarity(vectors[i], vectors[j]):.3f}  "
              f"'{sentences[i][:12]}' ↔ '{sentences[j][:12]}'")
```

---

## 12. FAISS 기본 RAG
> 예제: `1.openai/7.rag/1.rag_basic.py`

전체 파이프라인을 순수 OpenAI + FAISS로 한눈에:
**문서 → 임베딩 → FAISS 저장 → 질문 임베딩 → 유사 문서 검색 → GPT 응답**
```python
import os, numpy as np, faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

documents = [
    "Python은 강력한 프로그래밍 언어입니다.",
    "OpenAI는 AI 연구를 선도하는 기업입니다.",
    "FAISS는 벡터 검색을 위한 라이브러리입니다.",
]

def get_embedding(text):                                  # 텍스트 → 벡터
    r = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(r.data[0].embedding)

index = faiss.IndexFlatL2(1536)                           # L2 거리 인덱스(1536=차원)
index.add(np.array([get_embedding(d) for d in documents]))

def rag_query(user_query):
    q = get_embedding(user_query)                         # 질문도 같은 모델로 벡터화
    _, idx = index.search(np.array([q]), k=1)             # 가장 가까운 문서 1개
    retrieved = documents[idx[0][0]]

    prompt = f"참고 정보: {retrieved}\n\n질문: {user_query}\n답변:"   # ★ 검색문서를 프롬프트에 주입
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 친절한 AI 도우미입니다."},
            {"role": "user",   "content": prompt},
        ],
    )
    return r.choices[0].message.content

print(rag_query("Python은 어떤 언어인가요?"))
```

---

## 13. 텍스트 전처리 (청킹)
> 예제: `2.langchain/7.RAG/2.loaders/2.3_chunking.py`

**왜 청킹?** 임베딩 모델은 입력 길이 제한이 있고, 너무 큰 청크는 검색 정확도가
떨어지며(주제 혼재), 너무 작으면 맥락이 끊깁니다. 보통 200~1000 토큰 + overlap.
```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
    CharacterTextSplitter, RecursiveCharacterTextSplitter,
)

documents = TextLoader("../DATA/nvme.txt", encoding="utf-8").load()

# 1) Character — 정해진 separator로 단순 분할
char = CharacterTextSplitter(separator="\n\n", chunk_size=500, chunk_overlap=100)

# 2) Recursive — \n\n→\n→공백→글자 순으로 시도 (가장 권장되는 범용 splitter)
recur = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)

# 3) Token 기반 — tiktoken으로 실제 토큰 수 기준 (OpenAI 비용과 일치)
token = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=200, chunk_overlap=50)

for name, splitter in [("Character", char), ("Recursive", recur), ("Token", token)]:
    chunks = splitter.split_documents(documents)
    print(f"[{name}] {len(chunks)} 청크")
```
| 선택 | 추천 splitter |
|------|---------------|
| 일반 텍스트 | RecursiveCharacterTextSplitter |
| OpenAI 비용 관리 | from_tiktoken_encoder |
| 단순 데모 | CharacterTextSplitter |

---

## 14. LangChain RAG 체인
> 예제: `2.langchain/7.RAG/1.basics/1.3_first_rag.py`, `1.4_rag_lcel_chain.py`

검색 → 컨텍스트 합치기 → 프롬프트 주입 → LLM. (Day 2의 LCEL 그대로)
```python
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

docs = [
    Document(page_content="NVMe 는 SSD 의 인터페이스 규격으로 PCIe 를 사용한다."),
    Document(page_content="SATA SSD 는 NVMe 보다 속도가 느리다."),
    Document(page_content="HDD 는 회전 디스크 기반이라 IO 가 느린 편이다."),
]
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

query = "NVMe 와 SATA 의 차이?"
results = store.similarity_search(query, k=3)             # 유사 문서 검색
context = "\n".join(d.page_content for d in results)      # 컨텍스트로 합치기

prompt = ChatPromptTemplate.from_template(
    "아래 문서를 참고하여 질문에 답변하시오.\n\n문서:\n{context}\n\n질문:\n{question}"
)
chain = prompt | llm
print(chain.invoke({"context": context, "question": query}).content)
```

---

## 15. 벡터스토어 영속화와 표준 체인
> 예제: `2.langchain/7.RAG/3.vectorstore/3.1_persist.py`, `2.langchain/7.RAG/4.rag_chain/4.1_standard_chain.py`

### 15.1 ChromaDB 영속화 — 재실행 시 임베딩 비용 0
> InMemory는 프로세스 종료 시 사라져 매번 재임베딩(비용↑). Chroma는 디스크에 저장.
```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()
PERSIST_DIR, COLLECTION = "./chroma_db", "storage_demo"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
    store = Chroma(collection_name=COLLECTION, embedding_function=embeddings,
                   persist_directory=PERSIST_DIR)            # 기존 DB 로드(재임베딩 없음)
else:
    docs = TextLoader("../DATA/nvme.txt", encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)
    store = Chroma.from_documents(chunks, embeddings,        # 새로 생성 후 저장
                   collection_name=COLLECTION, persist_directory=PERSIST_DIR)

print(store.similarity_search("NVMe 의 인터페이스?", k=2))
```

### 15.2 표준 RAG 체인 — `RunnablePassthrough.assign`
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

retriever = store.as_retriever(search_kwargs={"k": 3})       # top-k 검색기
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages([
    ("system", "아래 문서만 참고해 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

# 입력 {"question":...}을 보존하며 검색 결과를 context로 추가 (Day 2의 9.3 패턴)
chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt | llm | StrOutputParser()
)
print(chain.invoke({"question": "NVMe 와 SATA SSD 의 차이?"}))
```

---

## 16. 대화형 RAG (history-aware)
> 예제: `2.langchain/7.RAG/5.conversational/5.3_full_conversational_rag.py`

문제: "그거 PCIe 몇 세대 써?" 같은 후속 질문은 맥락 없이 검색하면 실패합니다.
해결: 대화 이력으로 질문을 **독립 검색 쿼리로 재작성**한 뒤 검색.
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 1) 질문 재작성용 프롬프트 → history-aware retriever
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", "대화 이력과 이번 질문이 주어집니다. 이력 없이도 이해되는 독립 검색 쿼리로 다시 써주세요."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])
history_aware = create_history_aware_retriever(llm, retriever, rewrite_prompt)

# 2) 답변 생성 체인
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "아래 문서만 참고해 답하세요.\n\n문서:\n{context}"),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}"),
])
rag_chain = create_retrieval_chain(history_aware, create_stuff_documents_chain(llm, qa_prompt))

# 3) 세션 메모리 결합
sessions = {}
def get_history(sid):
    return sessions.setdefault(sid, InMemoryChatMessageHistory())

conversational_rag = RunnableWithMessageHistory(
    rag_chain, get_history,
    input_messages_key="input", history_messages_key="chat_history",
    output_messages_key="answer",
)

def chat(q):
    out = conversational_rag.invoke({"input": q}, config={"configurable": {"session_id": "demo"}})
    print(f"Q: {q}\nA: {out['answer']}")

chat("NVMe 가 뭐야?")
chat("그거 PCIe 몇 세대 쓰는데?")      # ← 맥락으로 정확히 검색
```

---

## 17. RAG 웹서비스
> 예제: `2.langchain/7.RAG/8.web_app/1.minimal/app.py`

Flask로 최소 MVP: `POST /upload`(문서 업로드→청킹→벡터DB) + `POST /ask`(질문→검색→답변).
```python
import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()
DATA_DIR, PERSIST_DIR, COLLECTION = "../DATA", "../chroma_db", "rag_web"
os.makedirs(DATA_DIR, exist_ok=True)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
store = Chroma(collection_name=COLLECTION, embedding_function=embeddings, persist_directory=PERSIST_DIR)
retriever = store.as_retriever(search_kwargs={"k": 5})
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 문서만 참고해서 답하세요. 문서에 없으면 '모르겠습니다'.\n\n문서:\n{context}"),
    ("user", "{question}"),
])
rag_chain = (
    RunnablePassthrough.assign(context=lambda x: format_docs(retriever.invoke(x["question"])))
    | prompt | llm | StrOutputParser()
)

def add_pdf(path):
    docs = PyPDFLoader(path).load()
    for d in docs:
        d.metadata["source"] = os.path.basename(path)
    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_documents(docs)
    store.add_documents(chunks)

app = Flask(__name__)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/upload")
def upload():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "파일이 없습니다"}), 400
    path = os.path.join(DATA_DIR, file.filename)
    file.save(path)
    add_pdf(path)
    return jsonify({"message": f"'{file.filename}' 업로드 완료"})

@app.post("/ask")
def ask():
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "질문이 없습니다"}), 400
    if store._collection.count() == 0:
        return jsonify({"answer": "먼저 PDF를 업로드해주세요."})
    return jsonify({"answer": rag_chain.invoke({"question": question})})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```
> 다음 단계: 유사도 점수·출처 표시(`4.refactor_with_score/`), 파일 추가/삭제, REST API + 정적 HTML 버전(`5.file_manager_restapi/`).

---

# 부록

## A. 환경 설정
`.env` (예제 폴더 기준 상위에 위치):
```
OPENAI_API_KEY=sk-...
```
```python
from dotenv import load_dotenv
load_dotenv()                      # 또는 load_dotenv(dotenv_path='../.env')
```

## B. 패키지 설치
```bash
# Day 1
pip install openai requests python-dotenv
# Day 2
pip install langchain langchain-openai langchain-community
# Day 3
pip install faiss-cpu numpy chromadb langchain-chroma langchain-text-splitters pypdf flask
```

## C. 모델 선택 빠른 가이드
| 용도 | 모델 |
|------|------|
| 채팅/RAG 생성 (기본) | `gpt-4o-mini` (저렴·빠름) |
| 임베딩 (기본) | `text-embedding-3-small` (1536차원) |
| 무료/로컬 임베딩 | `all-MiniLM-L6-v2`, `all-mpnet-base-v2` |

## D. 이론 교안 ↔ 코드 예제 매핑
| Day | 주제 | 이론(0.docs) | 코드 예제 |
|-----|------|-------------|-----------|
| 1 | 생성형 AI 기초 | `00_OT/05_generative_ai_intro.md` | — |
| 1 | REST API | `02_web_basics/05_http_protocol.md`, `03_python_webdev/13_external_api_and_gpt.md` | `1.openai/1.intro/1~4` |
| 1 | SDK·멀티턴 | — | `1.openai/1.intro/11,13`, `1.openai/3.chatbot2_history/` |
| 1 | 프롬프트 엔지니어링 | `01_genai_intro/04_prompt_engineering.md` | — |
| 1 | 컨텍스트 엔지니어링 | `01_genai_intro/05_so_what_now.md`, `05_genai_advanced/05_context_engineering.md` | — |
| 2 | LangChain | `05_genai_advanced/07_langchain_lcel.md` | `2.langchain/1~6` |
| 3 | 임베딩·벡터DB | `04_database/11_vector_databases.md` | `2.langchain/7.RAG/1.basics/`, `1.openai/7.rag/` |
| 3 | RAG 시스템 | `05_genai_advanced/06_rag_system.md` | `2.langchain/7.RAG/2~5` |
| 3 | RAG 웹앱 | — | `2.langchain/7.RAG/8.web_app/` |

## E. 전체 흐름 한눈에
```
[Day 1] 직접 REST 호출 → SDK → 멀티턴(messages 누적) → 프롬프트/컨텍스트 설계
            │  (반복되는 조립을 표준화하고 싶다)
            ▼
[Day 2] LangChain: Model · Prompt · Parser · Chain(LCEL |) · Memory
            │  (모델이 모르는 내 문서로 답하게 하고 싶다)
            ▼
[Day 3] 임베딩 → 청킹 → 벡터DB 검색 → 프롬프트 주입 → 생성(RAG)
            → 대화형 RAG → Flask 웹서비스
```
