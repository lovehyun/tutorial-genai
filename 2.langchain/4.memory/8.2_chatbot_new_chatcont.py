from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# 환경 변수 로드
load_dotenv()

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 2. 프롬프트 정의
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "너는 친절하고 똑똑한 AI야. 사용자의 질문에 친근하게 대답해."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}")
# ])

messages = [
    SystemMessagePromptTemplate.from_template("너는 친절하고 똑똑한 AI야. 사용자의 질문에 친근하게 대답해."),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
]
prompt = ChatPromptTemplate.from_messages(messages)


# 3. 체인 구성
chain = prompt | llm | StrOutputParser()

# 4. 단일 사용자 메모리 객체
memory = ChatMessageHistory()

# 5. 세션 ID는 아무 문자열이나 사용
session_id = "default"

# 6. 체인에 메모리 연결
chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,
    input_messages_key="input",
    history_messages_key="history"
)


# 8. 채팅 및 디버깅(메모리) 함수 정의
def chat(message: str) -> str:
    return chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )

def show_memory():
    print("\n-----\n현재 메모리 내용:")
    for msg in memory.messages:
        role = "사용자" if msg.type == "human" else "AI"
        print(f"{role}: {msg.content}")
    print("-----\n")


# 9. 대화
def main():
    print("AI 챗봇에 오신 걸 환영합니다! '종료' 를 입력하면 대화를 끝냅니다.")
    print("'메모리' 를 입력하면 지금까지의 대화 내용을 보여줍니다.\n")

    while True:
        user_input = input("나: ")
        if user_input.lower() in ["종료", "exit", "quit"]:
            print("대화를 종료합니다.")
            break

        if user_input.lower() in ["메모리", "memory"]:
            show_memory()
            continue

        response = chat(user_input)
        print("AI:", response)


# 10. 실행
if __name__ == "__main__":
    main()
