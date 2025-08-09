from dotenv import load_dotenv
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.output_parsers import StrOutputParser
# from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 0. .env 로드
load_dotenv()

# 1. 모델들 생성
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

# 2. 프롬프트 (요약 신뢰 지시 포함)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "너는 친절한 AI야. history에는 시스템 요약이 포함될 수 있다. "
        "요약의 사실을 신뢰하고 활용해 답하라."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# LLM 호출 시 
# 1. RunnableWithMessageHistory가 실행되면
#   - get_session_history() → 세션별 ChatMessageHistory 객체 반환
# 2. MessagesPlaceholder("history") 자리에
#   - mem.messages 리스트의 모든 메시지(SystemMessage, HumanMessage, AIMessage 등)가 역할(role)과 내용 그대로 들어감
# 3. LLM 호출 시
#   - OpenAI API에 전달되는 messages 필드에
#   [
#     {"role": "system", "content": "..."},
#     {"role": "human", "content": "..."},
#     {"role": "ai", "content": "..."},
#     ...
#   ]
#   이런 형태로 전부 포함됨


# 3. 체인
chain = prompt | llm | StrOutputParser()

# 4. 세션별 메모리 저장소
# sessions: dict[str, ChatMessageHistory] = {}
sessions: dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(arg):
    # langchain 버전에 따라 이 콜백에 세션ID 문자열이 오기도, 또는 dict가 오기도 함.
    """arg가 세션 ID 문자열이든, config dict든 모두 처리"""
    if isinstance(arg, str):
        session_id = arg
    else:
        # config 딕셔너리 형태일 때
        session_id = (arg.get("configurable", {}) or {}).get("session_id", "default")
        
    if session_id not in sessions:
        # sessions[session_id] = ChatMessageHistory()
        sessions[session_id] = InMemoryChatMessageHistory()
        
    return sessions[session_id]

# 5. 히스토리 포함 체인
chatbot_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 6. 세션별 요약 함수
def summarize_history_for_session(session_id: str, keep_last_turns: int = 1) -> str:
    mem = sessions[session_id]
    # 대화 요약 프롬프트 (핵심 사실 포함 지시)
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 대화를 핵심 사실(이름, 나이, 취미, 목표 등)을 잃지 않게 간결히 요약해줘."),
        ("human", "{dialogue}")
    ])
    summary_chain = summary_prompt | summarizer | StrOutputParser()
    dialogue_text = "\n".join(f"{m.type.upper()}: {m.content}" for m in mem.messages)
    summary = summary_chain.invoke({"dialogue": dialogue_text})

    # 요약 + 최근 N턴 보존 (N=1이면 Human, AI 2개 메시지)
    tail = mem.messages[-2 * keep_last_turns:] if keep_last_turns > 0 else []
    mem.clear()
    mem.add_message(SystemMessage(content=f"(요약) {summary}")) # 요약 내용은 시스템 메시지에 추가
    for m in tail:
        mem.add_message(m)

    return summary

# 7. 채팅 함수 (세션별)
def chat(message: str, session_id: str = "default"):
    print(f"[{session_id}] Q: {message}")
    
    resp = chatbot_chain.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )
    
    print(f"[{session_id}] A: {resp}")

    # 세션별 길이 기준 체크 (10개 초과 시 요약)
    mem = sessions[session_id]
    if len(mem.messages) > 10:
        print(f"\n[{session_id}] (대화 내용이 길어져서, 요약을 시작합니다...)")
        summary = summarize_history_for_session(session_id, keep_last_turns=1)
        print(f"[{session_id}] [자동 요약]: {summary}\n---\n")

    return resp


# 8. 데모: 두 명의 사용자(세션 A/B) 교차 대화 + 요약
if __name__ == "__main__":
    session_a = f"user-A-{uuid4().hex[:6]}"
    session_b = f"user-B-{uuid4().hex[:6]}"

    # 세션 A
    chat("안녕하세요, 제 이름은 김철수입니다.", session_a)
    chat("제 이름이 뭐였죠?", session_a)

    # 세션 B
    chat("안녕하세요, 제 이름은 고길동입니다.", session_b)
    chat("저는 여행 계획을 잘 세우고 싶어요.", session_b)

    # 세션 A
    chat("저는 요리를 배우고 싶어요.", session_a)
    chat("제가 무엇을 배우고 싶다고 했나요?", session_a)
    chat("그리고 제 나이는 35살이에요.", session_a)
    chat("제 나이가 몇 살이었죠?", session_a)  # -> 여기쯤 10개 초과되어 요약 트리거 예상
    chat("제 이름과 나이를 말해줄래요?", session_a)
    chat("제 취미는 등산입니다.", session_a)
    chat("제가 무슨 취미를 좋아한다고 했죠?", session_a)  

    # 세션 B
    chat("제 이름이 뭐였죠?", session_b)
    chat("여행 계획을 잘 세우려면 무엇부터 시작해야 하나요?", session_b)
    chat("제가 무엇을 배우고 있다고 했나요?", session_b)
    chat("제가 무엇을 하고 싶다고 했나요?", session_b)  # -> B도 일정 시점에서 요약 트리거 가능


    # 9) 디버깅: 세션 목록 + 트리 형태 로그
    print("\n=== 세션 목록 ===")
    for sid in sessions.keys():
        print(f"- {sid}")

    print("\n=== 세션별 대화 로그(트리) ===")
    for sid, mem in sessions.items():
        print(f"\n- 세션 ID: {sid}")
        for i, msg in enumerate(mem.messages, start=1):
            role = "[Human]" if msg.type == "human" else ("[AI]" if msg.type == "ai" else "[System]")
            print(f"   + {role}: {msg.content}")
