from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory

# 1. 환경 변수 로드
load_dotenv()

# 2. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 3. 프롬프트 정의 (수동 vs 라이브러리)
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a helpful assistant having a conversation."),
#     MessagesPlaceholder(variable_name="history"),  # 여기에 이전 대화 삽입됨
#     ("human", "{input}")
# ])

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful assistant having a conversation."),
    MessagesPlaceholder(variable_name="history"),  # 이전 대화가 리스트 형태로 들어감
    HumanMessage(content="{input}")
])


# 4. 체인 구성
chain = prompt | llm | StrOutputParser()

# 5. 초기 대화 기록 수동 생성
history = ChatMessageHistory()
history.add_user_message("Hello, Let's talk about giraffes")
history.add_ai_message("Sure! Giraffes are fascinating creatures.")

# 6. 새 사용자 입력
user_input = "What are they?"

# 7. (중요) 프롬프트에 실제로 들어갈 메시지 목록 확인
formatted_messages = prompt.format_messages(
    history=history.messages,
    input=user_input
)

print("\n--- 실제 프롬프트에 포함될 메시지 ---")
print(f"{formatted_messages}\n")
for msg in formatted_messages:
    role = msg.type.upper()
    content = msg.content
    print(f"{role}: {content}")

# 8. 체인 실행
response = chain.invoke({
    "history": history.messages,
    "input": user_input
})

# 9. 응답 출력
print("\n--- 사용자 질문 / AI 응답 ---")
print(f"Q: {user_input}")
print(f"A: {response}")

# 10. history 업데이트 (다음 대화를 위한 상태 유지)
history.add_user_message(user_input)
history.add_ai_message(response)

print("\n--- 다음 히스토리 ---")
print(history)


# =========================================================
# 11. 이어서 질문
next_input = "How tall are they?"

# 12. 디버깅: 실제 프롬프트 메시지 확인
print("\n--- 실제 프롬프트에 포함될 메시지 (2번째 질문) ---")
for msg in formatted_messages:
    print(f"{msg.type.upper()}: {msg.content}")

# 13. 체인 실행
next_response = chain.invoke({
    "history": history.messages,
    "input": next_input
})

print("\n--- 사용자 질문 / AI 응답 (2번째) ---")
print(f"Q: {next_input}")
print(f"A: {next_response}")

# 14. history 업데이트
history.add_user_message(next_input)
history.add_ai_message(next_response)

print("\n--- 최종 히스토리 ---")
for msg in history.messages:
    print(f"{msg.type.upper()}: {msg.content}")
