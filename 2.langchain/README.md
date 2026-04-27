# LangChain 예제

LangChain 프레임워크를 활용한 LLM 애플리케이션 개발 예제입니다.

## 학습 순서

| 디렉토리 | 주제 | 설명 |
|----------|------|------|
| `1.llm_models/` | LLM 모델 | OpenAI 모델 연동 (Completion, Chat, Flask) |
| `2.prompts/` | 프롬프트 | PromptTemplate, ChatPromptTemplate, 작업별 예제 |
| `3.structured_output/` | 구조화 출력 | StrOutputParser, Pydantic, with_structured_output |
| `4.chaining/` | 체이닝 | LCEL, RunnableLambda, RunnablePassthrough |
| `5.memory/` | 메모리 | 대화 히스토리 관리 (RunnableWithMessageHistory) |
| `6.RAG/` | RAG | 문서 검색 + LLM 응답 생성 파이프라인 |
| `7.agents/` | 에이전트 | 도구 사용 자율 에이전트 (검색, 위키, 커스텀) |
| `8.langgraph/` | LangGraph | 상태 기반 그래프 워크플로우 |

## 사전 준비

```bash
pip install langchain langchain-openai langchain-community langchain-text-splitters python-dotenv
```

---

## LangChain 라이브러리 아키텍처

### 패키지 버전 (2026년 4월 기준)

| 패키지 | 버전 | 역할 |
|--------|------|------|
| `langchain` | 1.2.15 | 에이전트 프레임워크 (create_agent, 미들웨어) |
| `langchain-core` | 1.3.2 | 핵심 추상화 (LCEL, Runnable, 메시지, 프롬프트) |
| `langchain-openai` | 1.2.1 | OpenAI 통합 (ChatOpenAI, OpenAIEmbeddings) |
| `langchain-anthropic` | 1.4.1 | Anthropic 통합 (ChatAnthropic) |
| `langchain-community` | 0.4.1 | 서드파티 통합 (문서 로더, 도구 등) |
| `langchain-google-genai` | 4.2.2 | Google Gemini 통합 |
| `langchain-chroma` | 1.1.0 | Chroma 벡터스토어 |
| `langchain-text-splitters` | 1.1.2 | 텍스트 분할 유틸리티 |
| `langgraph` | 1.1.10 | 그래프 기반 에이전트 오케스트레이션 |
| `openai` | 2.32.0 | OpenAI Python SDK |
| `anthropic` | 0.97.0 | Anthropic Python SDK |

### 패키지 계층 구조

```
langchain-core (핵심 추상화 + LCEL + Runnable 프로토콜)
    │
    ├── langchain (에이전트 프레임워크 + 미들웨어)
    │       └── langgraph (그래프 기반 실행 엔진)
    │
    ├── langchain-community (서드파티 통합)
    │
    ├── langchain-openai (OpenAI 전용)
    ├── langchain-anthropic (Anthropic 전용)
    ├── langchain-google-genai (Google Gemini 전용)
    ├── langchain-chroma (Chroma 벡터스토어)
    ├── langchain-text-splitters (텍스트 분할)
    └── langchain-classic (레거시 호환: LLMChain, ConversationBufferMemory 등)
```

**설계 원칙**: `langchain` v1.0은 `langgraph` 위에 구축되어 있다. 개발자는 LangChain의 고수준 API로 시작하여 필요시 LangGraph로 내려갈 수 있다.

---

### langchain-core 주요 모듈

`langchain-core`는 모든 LangChain 생태계의 기반이 되는 패키지로, 핵심 추상화를 정의한다.

| 모듈 | 역할 | 주요 클래스/함수 |
|------|------|-----------------|
| `messages` | 메시지 타입 | `HumanMessage`, `AIMessage`, `SystemMessage`, `ToolMessage` |
| `prompts` | 프롬프트 템플릿 | `ChatPromptTemplate`, `PromptTemplate`, `MessagesPlaceholder` |
| `output_parsers` | 출력 파서 | `StrOutputParser`, `JsonOutputParser`, `PydanticOutputParser` |
| `runnables` | LCEL 핵심 | `RunnableSequence`, `RunnableParallel`, `RunnablePassthrough`, `RunnableLambda` |
| `runnables.history` | 대화 히스토리 | `RunnableWithMessageHistory` |
| `chat_history` | 히스토리 저장 | `BaseChatMessageHistory`, `InMemoryChatMessageHistory` |
| `documents` | 문서 표현 | `Document` |
| `vectorstores` | 벡터스토어 인터페이스 | `VectorStore` (추상) |
| `retrievers` | 검색 인터페이스 | `BaseRetriever` (Runnable 구현) |
| `embeddings` | 임베딩 인터페이스 | `Embeddings` (추상) |
| `tools` | 도구 정의 | `tool` 데코레이터, `BaseTool` |
| `callbacks` | 이벤트 핸들러 | `CallbackHandler`, `CallbackManager` |

---

### LCEL (LangChain Expression Language)

LCEL은 LangChain의 핵심 프로그래밍 패러다임으로, 파이프(`|`) 연산자로 컴포넌트를 연결하여 체인을 구성한다.

#### Runnable 인터페이스

모든 LCEL 컴포넌트(프롬프트, LLM, 파서, 리트리버 등)가 구현하는 표준 인터페이스:

| 메서드 | 설명 |
|--------|------|
| `invoke(input)` | 동기 단건 실행 |
| `ainvoke(input)` | 비동기 단건 실행 |
| `stream(input)` | 동기 스트리밍 (토큰 단위) |
| `astream(input)` | 비동기 스트리밍 |
| `batch(inputs)` | 동기 배치 실행 |
| `abatch(inputs)` | 비동기 배치 실행 |

#### 파이프 연산자

```python
# Unix 파이프처럼 데이터가 왼쪽에서 오른쪽으로 흐른다
chain = prompt | model | output_parser
result = chain.invoke({"question": "LangChain이 뭐야?"})
```

#### 기본 체인 예시

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template("{topic}에 대해 설명해줘")
model = ChatOpenAI(model="gpt-4o")
parser = StrOutputParser()

chain = prompt | model | parser
result = chain.invoke({"topic": "인공지능"})
```

#### 주요 Runnable 타입

| 클래스 | 용도 | 예시 |
|--------|------|------|
| `RunnableSequence` | 순차 실행 (파이프로 자동 생성) | `prompt \| model \| parser` |
| `RunnableParallel` | 병렬 실행 | `{"context": retriever, "question": RunnablePassthrough()}` |
| `RunnablePassthrough` | 입력을 그대로 통과 | RAG에서 질문을 그대로 전달 |
| `RunnableLambda` | 일반 함수를 Runnable로 래핑 | `RunnableLambda(lambda x: x.upper())` |
| `RunnableWithMessageHistory` | 대화 히스토리 자동 관리 | 챗봇 구현 시 사용 |

#### RAG 체인 예시

```python
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
result = rag_chain.invoke("LangChain의 장점은?")
```

#### 대화 히스토리 예시

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 AI 어시스턴트입니다."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | model | StrOutputParser()

store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 사용
result = with_history.invoke(
    {"input": "안녕하세요!"},
    config={"configurable": {"session_id": "user1"}}
)
```

---

### 주요 import 경로 정리

#### 현재 표준 import

```python
# 메시지
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 프롬프트
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder

# 출력 파서
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

# Runnable
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

# 문서
from langchain_core.documents import Document

# 대화 히스토리
from langchain_core.chat_history import InMemoryChatMessageHistory

# LLM 모델
from langchain_openai import ChatOpenAI, OpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# 벡터스토어
from langchain_chroma import Chroma

# 텍스트 분할
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter

# 문서 로더
from langchain_community.document_loaders import TextLoader, PyPDFLoader, WebBaseLoader

# 에이전트
from langchain.agents import create_agent

# LangGraph
from langgraph.prebuilt import create_react_agent, ToolNode
from langgraph.graph import StateGraph, START, END, MessagesState
```

#### 레거시 → 현재 import 매핑

| 레거시 (v0.x) | 현재 (v1.x) |
|--------------|-------------|
| `from langchain.schema import HumanMessage` | `from langchain_core.messages import HumanMessage` |
| `from langchain.prompts import ChatPromptTemplate` | `from langchain_core.prompts import ChatPromptTemplate` |
| `from langchain.schema import Document` | `from langchain_core.documents import Document` |
| `from langchain.schema.runnable import RunnablePassthrough` | `from langchain_core.runnables import RunnablePassthrough` |
| `from langchain.text_splitter import RecursiveCharacterTextSplitter` | `from langchain_text_splitters import RecursiveCharacterTextSplitter` |
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |
| `from langchain.llms import OpenAI` | `from langchain_openai import OpenAI` |
| `from langchain.embeddings import OpenAIEmbeddings` | `from langchain_openai import OpenAIEmbeddings` |
| `from langchain.vectorstores import Chroma` | `from langchain_chroma import Chroma` |
| `from langchain.document_loaders import TextLoader` | `from langchain_community.document_loaders import TextLoader` |
| `from langchain.chains import LLMChain` | LCEL 체인으로 대체 (`prompt \| llm \| parser`) |
| `from langchain.memory import ConversationBufferMemory` | `RunnableWithMessageHistory` 사용 |
| `from langchain.agents import initialize_agent` | `from langchain.agents import create_agent` |

---

### 레거시 → 현재 API 마이그레이션

#### LLMChain → LCEL

```python
# 레거시
from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run("입력")

# 현재
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"variable": "입력"})
```

#### SequentialChain → RunnablePassthrough.assign()

```python
# 레거시
from langchain.chains import SequentialChain
overall_chain = SequentialChain(chains=[chain1, chain2], ...)

# 현재
from langchain_core.runnables import RunnablePassthrough
pipeline = (
    RunnablePassthrough.assign(step1_result=chain1)
    | RunnablePassthrough.assign(step2_result=chain2)
)
```

#### ConversationBufferMemory → RunnableWithMessageHistory

```python
# 레거시
from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory()

# 현재 → 위의 '대화 히스토리 예시' 참고
```

#### initialize_agent → create_agent

```python
# 레거시
from langchain.agents import initialize_agent, AgentType
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# 현재
from langchain.agents import create_agent
agent = create_agent(model=llm, tools=tools, prompt="You are a helpful assistant.")
result = agent.invoke({"messages": [{"role": "user", "content": "질문"}]})
```

#### RetrievalQA → LCEL RAG 체인

```python
# 레거시
from langchain.chains import RetrievalQA
qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

# 현재
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

---

### 설치 가이드

```bash
# 기본 설치
pip install langchain

# 프로바이더별 설치
pip install langchain-openai          # OpenAI
pip install langchain-anthropic       # Anthropic (Claude)
pip install langchain-google-genai    # Google Gemini

# 벡터스토어 / 텍스트 처리
pip install langchain-chroma          # Chroma 벡터스토어
pip install langchain-text-splitters  # 텍스트 분할
pip install langchain-community       # 커뮤니티 통합 (문서 로더 등)

# 그래프 기반 에이전트
pip install langgraph

# 레거시 호환 (구버전 코드 실행 필요시)
pip install langchain-classic
```
