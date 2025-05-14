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

# 대화 프롬프트 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI야."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# 체인 구성
chain = prompt | llm | StrOutputParser()

# 단일 사용자용 메모리 (세션 없음)
memory = ChatMessageHistory()

# 체인에 메모리 기능 결합
chain_with_memory = RunnableWithMessageHistory(
    chain,
    lambda _: memory,  # get_session_history_func 을 추가해야 하는 곳. (지금은 세션 구분 안하고 항상 같은 메모리 반환)
    input_messages_key="input",
    history_messages_key="history"
)

# 대화 시뮬레이션
print(chain_with_memory.invoke({"input": "안녕하세요"}, config={"configurable": {"session_id": "default"}}))
print(chain_with_memory.invoke({"input": "제 이름이 뭐였지요?"}, config={"configurable": {"session_id": "default"}}))
print(chain_with_memory.invoke({"input": "저는 프로그래밍을 배우고 싶어요."}, config={"configurable": {"session_id": "default"}}))
print(chain_with_memory.invoke({"input": "제가 무엇을 배우고 싶다고 했나요?"}, config={"configurable": {"session_id": "default"}}))
