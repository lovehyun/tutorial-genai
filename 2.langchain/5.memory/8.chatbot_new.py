from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory

# .env 파일에서 API 키 불러오기
load_dotenv()

# 1. LLM 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 2. 프롬프트 구성
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI야."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 3. 체인 구성
chain = prompt | llm | StrOutputParser()

# 4. 메모리 초기화 (단일 사용자용)
memory = ChatMessageHistory()

# 5. 기본 session_id 사용하여 대화 실행
session_id = "default"

# 6. 챗봇 체인 (세션 기반 메모리 포함)
# RunnableWithMessageHistory는 반드시 session_id를 필요로 함
chatbot = RunnableWithMessageHistory(
    chain,
    lambda _: memory,
    input_messages_key="input",
    history_messages_key="history"
)

# print(chatbot.invoke({"input": "안녕하세요, 제 이름은 김철수입니다."},
#                      config={"configurable": {"session_id": session_id}}))
# print(chatbot.invoke({"input": "제 이름이 뭐였죠?"},
#                      config={"configurable": {"session_id": session_id}}))
# print(chatbot.invoke({"input": "저는 요리를 배우고 싶어요."},
#                      config={"configurable": {"session_id": session_id}}))
# print(chatbot.invoke({"input": "제가 무엇을 배우고 싶다고 했나요?"},
#                      config={"configurable": {"session_id": session_id}}))

# 7. 간단한 chat 함수 정의
def chat(message: str) -> str:
    return chatbot.invoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    )

# 8. 대화 테스트
print(chat("안녕하세요, 제 이름은 김철수입니다."))
print(chat("제 이름이 뭐였죠?"))
print(chat("저는 요리를 배우고 싶어요."))
print(chat("제가 무엇을 배우고 싶다고 했나요?"))
