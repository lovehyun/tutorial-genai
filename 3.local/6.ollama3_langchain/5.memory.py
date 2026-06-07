# pip install langchain-ollama
#
# Ollama + LangChain 5: 대화 메모리.
# RunnableWithMessageHistory 로 세션별 대화 기록을 자동 주입한다.
# (LCEL 체인은 그대로, 히스토리만 래핑)

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

llm = ChatOllama(model="mistral")

prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 친절한 AI 어시스턴트다."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
chain = prompt | llm | StrOutputParser()

# 세션별 메모리 저장소
store = {}

def get_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

conversation = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "demo"}}

print(conversation.invoke({"input": "내 이름은 홍길동이야."}, config=config))
print(conversation.invoke({"input": "내 이름이 뭐였지?"}, config=config))  # 앞 대화를 기억
