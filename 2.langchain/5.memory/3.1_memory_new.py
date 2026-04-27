from dotenv import load_dotenv
import os, sys

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# 세션 개념이 없어서 모든 대화가 한 히스토리에 쌓입니다 → 여러 유저/세션을 지원하려면 세션별 히스토리 맵이 필요
# langchain_community.chat_message_histories.ChatMessageHistory는 구버전 느낌이라, 보통은 InMemoryChatMessageHistory(core)나 RunnableWithMessageHistory 사용을 권장

# 0. 환경 변수 로드
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY 미설정", file=sys.stderr); sys.exit(1)
    
# 1. OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 2. LangChain의 공식 메모리 기능 사용 (ChatMessageHistory)
# chat_history = ChatMessageHistory()
chat_history = InMemoryChatMessageHistory()

# 3. 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "답변은 간결하게 해주세요."),
    MessagesPlaceholder(variable_name="history"),  # 메시지 기록
    ("human", "{input}")
])

# prompt = ChatPromptTemplate.from_messages([
#     SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
#     MessagesPlaceholder(variable_name="history"),
#     HumanMessagePromptTemplate.from_template("{input}")
# ])

# 4. 체인 생성
chain = prompt | llm

# 5. 대화 수행

# 히스토리 내용 출력 함수
def print_history():
    print("\n===== 현재 메시지 히스토리 =====")
    for i, message in enumerate(chat_history.messages):
        role = "User" if message.type == "human" else "AI"
        print(f"{i+1}. {role}: {message.content}")
    print("================================\n")

def chat(message):
    # 현재 턴의 user 메시지는 {input}으로만 주고,
    # 호출 이후에 history에 추가 (중복 방지)
    
    print(f"Q: {message}")

    result = chain.invoke({
        "input": message,
        "history": chat_history.messages  # ChatMessageHistory에서 메시지 목록 가져오기
    })
    
    # 응답 출력
    print(f"A: {result.content}")
    
    # 대화 기록에 추가 (중복 방지: 호출 후에 저장)
    chat_history.add_user_message(message)
    chat_history.add_ai_message(result.content)
    
    # print_history()

# 6. 테스트
# chat("Hello")
# chat("Can we talk about sports?")
# chat("What's a good sport to play outdoor?")

chat("안녕하세요")
chat("운동에 대해서 이야기해 볼까요?")
chat("아웃도어 스포츠에 대해서 알려주세요.")
