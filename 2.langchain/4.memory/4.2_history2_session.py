from dotenv import load_dotenv
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


# .env 파일 로드
load_dotenv()

# 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 프롬프트 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI야."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 체인 구성
chain = prompt | llm | StrOutputParser()

# 세션별 대화 기록 저장소
history = {}

def get_session_history(session_id):
    if session_id not in history:
        # history[session_id] = ChatMessageHistory() # 세선 관리 메모리 새로 생성
        history[session_id] = InMemoryChatMessageHistory() # 세선 관리 메모리 새로 생성
        
    return history[session_id]

# 메시지 히스토리를 포함한 체인 구성
chain_with_memory = RunnableWithMessageHistory(
    chain,
    lambda session_id: get_session_history(session_id),
    input_messages_key="input",
    history_messages_key="history"
)

# 채팅 함수
def chat(message, session_id):
    print(f"Q: {message}")
    response = chain_with_memory.invoke({"input": message}, config={"configurable": {"session_id": session_id}})
    print(f"A: {response}")
    return response

# 대화 시뮬레이션
session_id1 = str(uuid4()) # 세션 ID 지정
session_id2 = str(uuid4())

chat("안녕하세요", session_id1)
chat("제 이름이 뭐였지요?", session_id1)
chat("제 이름은 홍길동 이에요", session_id1)
chat("저는 프로그래밍을 배우고 싶어요.", session_id1)
chat("저는 누구고 무엇을 배우고 싶다고 했나요?", session_id1)

chat("제 이름은 고길동 이에요", session_id2)
chat("저는 누구고 무엇을 배우고 싶다고 했나요?", session_id2)

# print(history)
