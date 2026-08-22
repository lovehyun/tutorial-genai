# LLM 2일차: LangChain 개요 & LCEL 기본기

## 학습 목표
- LangChain 핵심 구성(LLM, Prompt, Output Parser, Runnables, Memory)을 이해하고 직접 체인을 만듭니다.
- **LCEL(LangChain Expression Language)**로 직관적인 파이프라인을 설계합니다.
- 동기/비동기, 배치/스트리밍, 히스토리 관리까지 실습합니다.

---

## 설치
```bash
pip install langchain langchain-openai langchain-community tiktoken python-dotenv
```

## 필수 import
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
```

---

## LangChain 구성요소 한눈에
- **LLM/ChatModel**: `ChatOpenAI(model="gpt-4o-mini")`
- **Prompt**: `ChatPromptTemplate.from_messages([...])`
- **Parser**: `StrOutputParser()`, `PydanticOutputParser(...)`
- **Runnable**: `|` 로 연결되는 실행 가능한 조각
- **Memory**: 대화 이력 상태 관리(요약/버퍼 등)

### 가장 작은 체인
```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
prompt = ChatPromptTemplate.from_template("한 문장으로 {topic}를 설명하세요.")
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"topic":"강화학습"}))
```

### 데이터 전처리와 결합
```python
def normalize_topic(x: dict):
    t = x["topic"].strip().lower()
    return {"topic": t}

pre = RunnablePassthrough.assign(**{"topic": lambda x: x["topic"].strip()})
chain = pre | prompt | llm | StrOutputParser()
```

---

## 스트리밍(토큰 단위)
```python
import asyncio

async def astream_example():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    prompt = ChatPromptTemplate.from_template("{q}")
    chain = prompt | llm | StrOutputParser()
    async for chunk in chain.astream({"q":"토마토로 만드는 파스타를 요약"}):
        print(chunk, end="", flush=True)

asyncio.run(astream_example())
```

---

## 배치 실행 & 병렬
```python
questions = [
    {"q":"마르코프 체인 한줄 요약"},
    {"q":"KL divergence 직관"},
    {"q":"L2 정규화 효과"}
]

chain = (ChatPromptTemplate.from_template("{q}")
         | ChatOpenAI(model="gpt-4o-mini")
         | StrOutputParser())

# 동기 배치
print(chain.batch(questions))

# 비동기 배치
import asyncio
async def run_batch():
    results = await chain.abatch(questions)
    for r in results:
        print(r)
asyncio.run(run_batch())
```

---

## 메모리(대화 히스토리)
간단하게는 **버퍼 메모리**를 사용합니다. 고급은 `RunnableWithMessageHistory`.

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = ChatOpenAI(model="gpt-4o-mini")
memory = ConversationBufferMemory(return_messages=True)
conv = ConversationChain(llm=llm, memory=memory, verbose=False)

print(conv.run("안녕하세요, 오늘 날씨 어때요?"))
print(conv.run("그럼 우산 가져갈까요?"))
```

### RunnableWithMessageHistory
```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "항상 존댓말로 답하세요."),
    ("human", "{input}")
])

llm = ChatOpenAI(model="gpt-4o-mini")
chain = prompt | llm | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input"
)

print(chain_with_history.invoke(
    {"input":"내일 부산 일정 추천해 주세요."},
    config={"configurable":{"session_id":"user-1"}}
))
```

---

## 출력 파서 다양화
- `StrOutputParser()` → 순수 텍스트
- `JsonOutputParser()` → JSON 파싱
- `PydanticOutputParser()` → 스키마 검증

```python
from pydantic import BaseModel
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_template(
    "다음 키를 포함한 JSON으로 답하세요: title, bullets(리스트). 주제: {topic}"
)
chain = prompt | llm | JsonOutputParser()
print(chain.invoke({"topic":"스터디 운영 요령"}))
```

---

## 실습 과제
1) `RunnableWithMessageHistory` 기반 간단 챗봇 작성(세션 분리).  
2) 같은 프롬프트로 `StrOutputParser`/`JsonOutputParser`/`PydanticOutputParser` 결과 비교.  
3) `astream`으로 스트리밍 출력 UI를 콘솔에 구현.

---

## 자주 겪는 문제
- **빈 응답**: temperature=0로, 프롬프트에 **역할/포맷** 명시 강화
- **한글 깨짐**: 콘솔/파일 인코딩 `utf-8` 지정
- **세션 충돌**: 세션 키 분리, 메모리 저장소 격리
