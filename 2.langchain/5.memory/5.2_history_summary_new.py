from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
# from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# 0. .env 로드
load_dotenv()

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. 프롬프트 구성
# prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template("너는 친절한 AI야."),
#     MessagesPlaceholder(variable_name="history"),
#     HumanMessagePromptTemplate.from_template("{input}")
# ])

# 2. 프롬프트 구성 (요약 신뢰 지시 추가)
prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "너는 친절한 AI야. history에는 시스템 요약이 포함될 수 있다."
        "요약의 사실을 신뢰하고 활용해 답하라."
    ),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# 3. 체인 구성
chain = prompt | llm | StrOutputParser()

# 4. 메모리 구성 (단일 세션)
# memory = ChatMessageHistory()
memory = InMemoryChatMessageHistory()

# RunnableWithMessageHistory 구성
chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,
    input_messages_key="input",
    history_messages_key="history"
)

# 5. 요약용 LLM
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def summarize_history():
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "다음 대화의 핵심 사실(이름, 나이, 취미 등)을 잃지 않도록 간결하게 요약하세요."),
        ("human", "{dialogue}")
    ])
    summary_chain = (summary_prompt | summarizer | StrOutputParser())
    dialogue_text = "\n".join([f"{m.type.upper()}: {m.content}" for m in memory.messages])
    return summary_chain.invoke({"dialogue": dialogue_text})

def chat(message: str, session_id="default"):
    """Q/A 출력 + 자동 요약"""
    print(f"Q: {message}")
    response = chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )
    print(f"A: {response}")

    # 대화 길이 제한 체크 (예: 10개 메시지 초과 시 요약)
    if len(memory.messages) > 10:
        print("(대화 내용이 길어져서, 요약을 시작합니다...)")
        print("\n[자동 요약 실행]")
        summary = summarize_history()
        print(f"[요약 내용]: {summary}")
        
        # 메모리 초기화 후 요약만 저장
        # memory.clear()
        # memory.add_message(SystemMessage(content=f"(요약) {summary}"))

        # 요약 + 최근 1턴 보존
        tail = memory.messages[-2:]  # Human, AI 한 쌍
        memory.clear()
        memory.add_message(SystemMessage(content=f"(요약) {summary}"))
        for m in tail:
            memory.add_message(m)

    return response


# 테스트
chat("안녕하세요, 제 이름은 김철수입니다.")
chat("제 이름이 뭐였죠?")
chat("저는 요리를 배우고 싶어요.")
chat("제가 무엇을 배우고 싶다고 했나요?")
chat("그리고 제 나이는 35살이에요.")
chat("제 나이가 몇 살이었죠?")  # → 6번째 질문. 여기서 요약 트리거 (10개 = 5쌍)
chat("제 이름과 나이를 말해줄래요?")
chat("제 취미는 등산입니다.")
chat("제가 무슨 취미를 좋아한다고 했죠?")
chat("제가 지금까지 말한 걸 모두 말해줄래요?") # 추가 4번째 질문. 여기서 요약 트리거 (기존 1쌍 + 추가 4쌍)
chat("제 이름만 다시 말해줄래요?")  
