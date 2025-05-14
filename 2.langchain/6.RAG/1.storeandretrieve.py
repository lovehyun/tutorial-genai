from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# 1. 환경 변수 로드
load_dotenv()

# 2. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 3. 프롬프트 정의
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant having a conversation."),
    MessagesPlaceholder(variable_name="history"),  # 여기에 이전 대화 삽입됨
    ("human", "{input}")
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

print("\n실제 프롬프트에 포함될 메시지:")
for msg in formatted_messages:
    role = msg.type.upper()
    print(f"{role}: {msg.content}")

# 8. 체인 실행
response = chain.invoke({
    "history": history.messages,
    "input": user_input
})

# 9. 응답 출력
print("\nAI 응답:")
print(response)

# 10. history 업데이트 (다음 대화를 위한 상태 유지)
history.add_user_message(user_input)
history.add_ai_message(response)
