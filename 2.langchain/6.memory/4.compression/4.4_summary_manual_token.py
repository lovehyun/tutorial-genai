"""
tiktoken 으로 직접 토큰 계산 → 임계치 초과 시 요약 (참고용)

  ※ 실무에선 4.1 의 trim_messages 를 먼저 검토하세요. LangChain 빌트인이라 더 깔끔합니다.
     이 파일은 "라이브러리 도움 없이 토큰을 직접 다루는 방법" 을 보여주는 학습용.

핵심:
  - tiktoken 으로 메시지 텍스트의 토큰 수를 계산
  - MAX_HISTORY_TOKENS 초과 시 요약하고 최근 N 턴만 보존
"""

from dotenv import load_dotenv
import tiktoken
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage

load_dotenv()

MODEL_NAME         = "gpt-4o-mini"
MAX_HISTORY_TOKENS = 200       # 임계치 (예제용으로 일부러 작게)
KEEP_LAST_TURNS    = 1

llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
try:
    enc = tiktoken.encoding_for_model(MODEL_NAME)
except KeyError:
    enc = tiktoken.get_encoding("cl100k_base")


prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 친절한 어시스턴트입니다. '(요약)' 시스템 메시지가 있다면 신뢰하세요."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()


def count_tokens(messages) -> int:
    return sum(len(enc.encode(m.content)) for m in messages)


def summarize_if_needed():
    if count_tokens(memory.messages) <= MAX_HISTORY_TOKENS:
        return
    dialogue = "\n".join(f"{m.type.upper()}: {m.content}" for m in memory.messages)
    summary = (
        ChatPromptTemplate.from_messages([
            ("system", "다음 대화의 핵심 사실을 간결히 요약하세요."),
            ("human", "{dialogue}"),
        ])
        | llm | StrOutputParser()
    ).invoke({"dialogue": dialogue})

    tail = memory.messages[-2 * KEEP_LAST_TURNS:]
    memory.clear()
    memory.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        memory.add_message(m)
    print(f"  ↳ [요약 트리거] 압축 후 토큰: {count_tokens(memory.messages)}")


with_history = RunnableWithMessageHistory(
    chain, lambda _: memory,
    input_messages_key="input",
    history_messages_key="history",
)


def chat(message):
    print(f"\nQ: {message}  (현재 토큰: {count_tokens(memory.messages)})")
    summarize_if_needed()
    answer = with_history.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}},
    )
    print(f"A: {answer}")


chat("제 이름은 김철수예요.")
chat("저는 35살이고 등산이 취미예요.")
chat("강아지를 키우는데 이름은 뽀삐예요.")
chat("저는 개발자로 일해요.")
chat("최근 설악산 다녀왔는데 정말 좋았어요.")
chat("제 이름과 취미가 뭐였죠?")
