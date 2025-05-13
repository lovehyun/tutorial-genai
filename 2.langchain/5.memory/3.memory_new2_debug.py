from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, verbose=True)  # verbose=True 추가

# LangChain의 공식 메모리 기능 사용 (ChatMessageHistory)
message_history = ChatMessageHistory()

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),  # 메시지 기록
    ("human", "{input}")
])

# 체인 생성
chain = prompt | llm

# 히스토리 내용 출력 함수
def print_history():
    print("\n===== 현재 메시지 히스토리 =====")
    for i, message in enumerate(message_history.messages):
        role = "User" if message.type == "human" else "AI"
        print(f"{i+1}. {role}: {message.content}")
    print("================================\n")

# 대화 수행
def chat(message):
    print(f"\n>>> 사용자 입력: {message}")
    
    # 체인 실행 전 현재 히스토리 출력
    print_history()
    
    # 현재 히스토리 메시지와 함께 입력될 프롬프트 내용 출력
    print(">>> 프롬프트에 전달되는 내용:")
    
    # 프롬프트 내용 출력 (messages 객체로 변환)
    messages_for_prompt = prompt.format_messages(
        input=message, 
        history=message_history.messages
    )
    
    # 프롬프트 메시지 출력 (보기 좋게 형식화)
    for msg in messages_for_prompt:
        print(f"Role: {msg.type}, Content: {msg.content[:100]}...")
    
    # 체인 실행 (메시지 기록 포함)
    result = chain.invoke({
        "input": message,
        "history": message_history.messages
    })
    
    print(f">>> AI 응답: {result.content}")
    
    # 메시지 기록 업데이트
    message_history.add_user_message(message)
    message_history.add_ai_message(result.content)
    
    return result.content

# 테스트
print(chat("Hello"))
print(chat("Can we talk about sports?"))
print(chat("What's a good sport to play outdoor?"))
