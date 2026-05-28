"""
대화 자동 요약 — 길어지면 LLM 으로 요약 후 압축 (단일 세션)

trim_messages 가 단순히 자르는 데 비해, 요약은 오래된 메시지를 LLM 으로 압축해
"(요약) ..." SystemMessage 한 줄에 핵심 사실을 보존합니다.
대신 LLM 추가 호출 비용이 발생합니다.

  - 4.2 (이 파일) : 단일 세션 + 자동 요약
  - 4.3            : 멀티 세션 확장
  - 4.4            : tiktoken 으로 직접 토큰 계산 (참고용)
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage

load_dotenv()
llm        = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 친절한 한국어 어시스턴트입니다. "
     "history 에 '(요약)' 으로 시작하는 시스템 메시지가 있다면 그 사실을 신뢰해 답하세요."),
    MessagesPlaceholder("history"),
    ("user", "{input}"),
])
chain = prompt | llm | StrOutputParser()

memory = InMemoryChatMessageHistory()
chatbot = RunnableWithMessageHistory(
    chain, lambda _: memory,
    input_messages_key="input",
    history_messages_key="history",
)

# 요약 체인
summary_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "다음 대화에서 핵심 사실(이름, 나이, 취미 등)을 잃지 않도록 간결히 요약하세요."),
        ("human", "{dialogue}"),
    ])
    | summarizer
    | StrOutputParser()
)

MAX_MSGS = 8   # 메시지 수가 이 이상이면 요약 트리거 (1 턴 = 2 개)


def summarize_and_compress():
    """오래된 대화를 요약하고, 최근 1 턴만 남김"""
    dialogue = "\n".join(f"{m.type.upper()}: {m.content}" for m in memory.messages)
    summary = summary_chain.invoke({"dialogue": dialogue})

    tail = memory.messages[-2:]      # 최근 Human + AI 보존
    memory.clear()
    memory.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        memory.add_message(m)
    return summary


def chat(message):
    print(f"\nQ: {message}")
    answer = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": "default"}},
    )
    print(f"A: {answer}")

    if len(memory.messages) > MAX_MSGS:
        s = summarize_and_compress()
        print(f"  ↳ [자동 요약] {s}")


chat("제 이름은 김철수예요.")
chat("저는 35살이고 등산이 취미예요.")
chat("강아지를 키워요. 이름은 뽀삐예요.")
chat("저는 개발자로 일하고 있어요.")
chat("제 이름이 뭐였죠?")          # ← 요약 트리거 직전 (메시지 8 → 10)
chat("제 강아지 이름이 뭐였죠?")    # ← 요약 발생 후에도 정확히 기억해야 정상
