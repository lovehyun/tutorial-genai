from dotenv import load_dotenv

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv(dotenv_path='../.env')

# 초기 대화 기록 생성
history = ChatMessageHistory()
history.add_user_message("Hello, Let's talk about giraffes")
history.add_ai_message("Hello, I'm down to talk about giraffes")

# 대화 기록 출력
messages = history.messages
print([{"type": msg.type, "content": msg.content} for msg in messages])

# ChatOpenAI 모델 설정
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 프롬프트 템플릿 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant having a conversation."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 체인 생성
chain = prompt | llm

# 대화 실행
response = chain.invoke({
    "history": messages,
    "input": "What are they?"
})

print(response.content)
