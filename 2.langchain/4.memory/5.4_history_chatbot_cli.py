from dotenv import load_dotenv
import os, sys

from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import SystemMessage

# =========================
# 0. 환경
# =========================
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY가 설정되지 않았습니다.", file=sys.stderr)
    sys.exit(1)

# =========================
# 1. 모델
# =========================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# =========================
# 2. 프롬프트 (요약 신뢰 지시 포함)
# =========================
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "너는 친절하고 똑똑한 AI야. 사용자의 질문에 친근하게 대답해."
        "history에는 시스템 요약이 포함될 수 있다. 요약의 사실을 신뢰하고 활용해 답하라."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

chain = prompt | llm | StrOutputParser()

# =========================
# 3. 메모리 & 체인 (단일 세션)
# =========================
memory = InMemoryChatMessageHistory()
session_id = "default"

chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,               # 단일 세션이므로 항상 같은 메모리
    input_messages_key="input",
    history_messages_key="history",
)

# =========================
# 4. 요약 도구
# =========================
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "다음 대화를 핵심 사실(이름, 나이, 취미, 목표 등)을 잃지 않게 간결히 요약해줘."),
    ("human", "{dialogue}")
])
summary_chain = summary_prompt | summarizer | StrOutputParser()

def summarize_and_compress(keep_last_turns: int = 1) -> str:
    """대화가 길어지면: 요약(System) + 최근 N턴 보존"""
    dialogue_text = "\n".join(f"{m.type.upper()}: {m.content}" for m in memory.messages)
    summary = summary_chain.invoke({"dialogue": dialogue_text})

    # 최근 N턴 보존 (Human+AI = 2*N 메시지)
    tail = memory.messages[-2 * keep_last_turns:] if keep_last_turns > 0 else []
    memory.clear()
    memory.add_message(SystemMessage(content=f"(요약) {summary}"))
    for m in tail:
        memory.add_message(m)
    return summary

# =========================
# 5. 유틸: 디버그 표시
# =========================
def show_memory():
    print("\n----- 현재 메모리 내용 -----")
    for i, msg in enumerate(memory.messages, start=1):
        role = "System" if msg.type == "system" else ("사용자" if msg.type == "human" else "AI")
        print(f"{i:02d}. [{role}] {msg.content}")
    print("---------------------------\n")

def show_summary():
    sys_msgs = [m for m in memory.messages if m.type == "system"]
    if not sys_msgs:
        print("\n(요약 System 메시지가 없습니다.)\n")
        return
    print("\n----- 최신 요약(System) -----")
    print(sys_msgs[-1].content)
    print("----------------------------\n")

# =========================
# 6. 채팅 함수
# =========================
MAX_MSGS = 10  # 메시지 수 임계치(요약 트리거)

def chat(user_input: str) -> str:
    print(f"\nQ: {user_input}")
    resp = chatbot.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    print(f"A: {resp}")

    # 자동 요약 트리거
    if len(memory.messages) > MAX_MSGS:
        print("\n(대화 내용이 길어져서, 요약을 시작합니다...)")
        summary = summarize_and_compress(keep_last_turns=1)
        print(f"[자동 요약]: {summary}\n")

    return resp

# =========================
# 7. CLI 루프
# =========================
def main():
    print("AI 챗봇에 오신 걸 환영합니다! '종료' 종료, '메모리' 대화목록, '요약' 최신요약, '임계' 임계치 확인/변경")
    print("예) 임계 12  → 메시지 12개 초과 시 요약\n")

    while True:
        try:
            user_input = input("나: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            break

        if not user_input:
            continue

        low = user_input.lower()
        if low in {"종료", "exit", "quit"}:
            print("대화를 종료합니다.")
            break
        if low in {"메모리", "memory"}:
            show_memory()
            continue
        if low in {"요약", "summary"}:
            show_summary()
            continue
        if low.startswith("임계"):
            parts = user_input.split()
            if len(parts) == 2 and parts[1].isdigit():
                global MAX_MSGS
                MAX_MSGS = int(parts[1])
                print(f"(요약 임계치를 {MAX_MSGS}로 설정했습니다.)")
            else:
                print(f"(현재 요약 임계치: {MAX_MSGS})  예) 임계 12")
            continue

        # 일반 대화
        try:
            chat(user_input)
        except Exception as e:
            print(f"(에러) {e}")

if __name__ == "__main__":
    main()
