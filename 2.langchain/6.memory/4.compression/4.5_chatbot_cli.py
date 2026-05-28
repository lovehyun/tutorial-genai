"""
종합 응용 — 자동 요약 챗봇 CLI

지금까지 배운 것을 합친, 실제로 돌릴 수 있는 챗봇:
  - RunnableWithMessageHistory 로 자동 메모리
  - 메시지 수 임계치 초과 시 자동 요약 + 압축
  - CLI 명령:  '메모리'(메모리 보기) / '요약'(최신 요약) / '종료'
"""

import sys, os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY 미설정", file=sys.stderr); sys.exit(1)

llm        = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 친절한 한국어 어시스턴트입니다. "
     "history 에 '(요약)' 시스템 메시지가 있다면 그 사실을 신뢰해 답하세요."),
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

summary_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "다음 대화의 핵심 사실(이름, 나이, 취미 등)을 잃지 않게 간결히 요약하세요."),
        ("human", "{dialogue}"),
    ])
    | summarizer | StrOutputParser()
)

MAX_MSGS = 10


def summarize_and_compress():
    dialogue = "\n".join(f"{m.type.upper()}: {m.content}" for m in memory.messages)
    summary = summary_chain.invoke({"dialogue": dialogue})
    tail = memory.messages[-2:]
    memory.clear()
    memory.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        memory.add_message(m)
    return summary


def show_memory():
    print("\n----- 현재 메모리 -----")
    for i, m in enumerate(memory.messages, 1):
        role = {"system": "System", "human": "User", "ai": "AI"}.get(m.type, m.type)
        print(f"{i:02d}. [{role}] {m.content}")
    print("------------------------")


def show_summary():
    sys_msgs = [m for m in memory.messages if m.type == "system"]
    if sys_msgs:
        print(f"\n[최신 요약] {sys_msgs[-1].content}")
    else:
        print("\n(요약이 아직 없습니다.)")


def main():
    print("챗봇 시작. 명령: 메모리 / 요약 / 종료")
    while True:
        try:
            user_in = input("\n나: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break
        if not user_in:
            continue
        if user_in in {"종료", "exit", "quit"}:
            print("종료합니다."); break
        if user_in == "메모리":
            show_memory(); continue
        if user_in == "요약":
            show_summary(); continue

        try:
            answer = chatbot.invoke(
                {"input": user_in},
                config={"configurable": {"session_id": "default"}},
            )
            print(f"AI: {answer}")
            if len(memory.messages) > MAX_MSGS:
                s = summarize_and_compress()
                print(f"  ↳ [자동 요약] {s}")
        except Exception as e:
            print(f"(에러) {e}")


if __name__ == "__main__":
    main()
