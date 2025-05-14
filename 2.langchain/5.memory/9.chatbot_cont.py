from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# 환경 변수 로드
load_dotenv()

# LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 프롬프트 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절하고 똑똑한 AI야. 사용자의 질문에 친근하게 대답해."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 체인 구성
chain = prompt | llm | StrOutputParser()

# 단일 사용자 메모리 객체
memory = ChatMessageHistory()

# 체인에 메모리 연결
chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,
    input_messages_key="input",
    history_messages_key="history"
)

# 세션 ID는 아무 문자열이나 사용
session_id = "default"

print("AI 챗봇에 오신 걸 환영합니다! '종료' 를 입력하면 대화를 끝냅니다.")
print("'메모리' 를 입력하면 지금까지의 대화 내용을 보여줍니다.\n")

while True:
    user_input = input("나: ")
    
    if user_input.lower() in ["종료", "exit", "quit"]:
        print("대화를 종료합니다.")
        break

    if user_input.lower() in ["메모리", "memory"]:
        print("\n-----\n현재 메모리 내용:")
        for msg in memory.messages:
            role = "사용자" if msg.type == "human" else "AI"
            print(f"{role}: {msg.content}")
        print("-----\n")
        continue

    response = chatbot.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )
    print("AI:", response)
