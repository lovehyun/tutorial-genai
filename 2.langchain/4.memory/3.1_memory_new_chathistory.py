from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
# 환경 변수 로드
load_dotenv()

# OpenAI 채팅 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# LangChain의 공식 메모리 기능 사용 (ChatMessageHistory)
chat_history = ChatMessageHistory()

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),  # 메시지 기록
    ("human", "{input}")
])

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{input}")
])

# 체인 생성
chain = prompt | llm

# 대화 수행
def chat(message):
    # 체인 실행 (메시지 기록 포함)
    result = chain.invoke({
        "input": message,
        "history": chat_history.messages  # ChatMessageHistory에서 메시지 목록 가져오기
    })
    
    # 메시지 기록 업데이트 (LangChain 공식 메모리 기능 사용)
    chat_history.add_user_message(message)
    chat_history.add_ai_message(result.content)
    
    return result.content

# 테스트
print(chat("Hello"))
print(chat("Can we talk about sports?"))
print(chat("What's a good sport to play outdoor?"))
