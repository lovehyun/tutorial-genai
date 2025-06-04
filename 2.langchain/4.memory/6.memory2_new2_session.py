from dotenv import load_dotenv
from uuid import uuid4

from langchain_openai import ChatOpenAI

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# .env 파일 로드
load_dotenv()

# 모델 초기화
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# 프롬프트 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI야."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 체인 구성
chain = prompt | llm | StrOutputParser()

# 세션 ID 지정
session_id = str(uuid4())

# 세션별 대화 기록 저장소
store = {}

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 메시지 히스토리를 포함한 체인 구성
chain_with_memory = RunnableWithMessageHistory(
    chain,
    lambda session_id: get_session_history(session_id),
    input_messages_key="input",
    history_messages_key="history"
)

# print(chain_with_memory.invoke({"input": "안녕하세요, 제 이름은 김철수입니다."}, config={"configurable": {"session_id": session_id}}))
# print(chain_with_memory.invoke({"input": "제 이름이 뭐였지요?"}, config={"configurable": {"session_id": session_id}}))
# print(chain_with_memory.invoke({"input": "저는 프로그래밍을 배우고 싶어요."}, config={"configurable": {"session_id": session_id}}))
# print(chain_with_memory.invoke({"input": "제가 무엇을 배우고 싶다고 했나요?"}, config={"configurable": {"session_id": session_id}}))

# 채팅 함수
def chat(message, session_id):
    return chain_with_memory.invoke({"input": message}, config={"configurable": {"session_id": session_id}})

# 대화 실행
print(chat("안녕하세요, 제 이름은 김철수입니다.", session_id))
print(chat("제 이름이 뭐였지요?", session_id))
print(chat("저는 프로그래밍을 배우고 싶어요.", session_id))
print(chat("제가 무엇을 배우고 싶다고 했나요?", session_id))
